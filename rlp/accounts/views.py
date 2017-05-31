from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, authenticate)
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.core import signing
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import inlineformset_factory
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from actstream.models import Action
from el_pagination.decorators import page_template
from formtools.wizard.views import SessionWizardView

from casereport.constants import WorkflowState
from casereport.models import CaseReport
from rlp.accounts.models import Institution
from rlp.bibliography.models import fetch_publications_for_user
from rlp.bibliography.models import Reference
from rlp.core.email import send_transactional_mail
from rlp.core.views import MESSAGES_DEFAULT_FORM_ERROR
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document
from rlp.projects.models import Project, ProjectMembership
from rlp.search.forms import ActionObjectForm, ProjectContentForm

from .forms import RegistrationForm, UserProfileForm, AuthenticationForm, ProjectMembershipForm, \
    RestrictedProjectMembershipForm
from .models import User
from .signals import sync_user

REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')

REGISTRATION_SUCCESS_SUBJECT = "Thank you for registering"
PENDING_APPROVAL_SUBJECT = '{}: New registration pending approval'.format(settings.SITE_PREFIX.upper())
PENDING_REGISTRATION_MESSAGE = "Thank you for your interest in joining the {} Research Network. " \
                               "Your registration is pending approval. You will receive an email when your " \
                               "registration is complete.".format(settings.SITE_PREFIX.upper())


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='accounts/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    Borrowed from ``django.contrib.auth.views.login`` but customized for the following reasons:
        * Don't show the login form to users who are logged in already
        * We had some bugs which didn't capture data that we should have captured.
          For these users we manually logged them out so that the next time they login, we can
          redirect them to their profile page with an appropriate message.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))
    # This is a customization, not sure why Django doesn't do this already
    # but if the user is already logged in, why would we show them the login form?
    if request.user.is_authenticated():
        if redirect_to and is_safe_url(url=redirect_to, host=request.get_host()):
            return redirect(redirect_to)
        else:
            return redirect('dashboard')

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if redirect_to and not is_safe_url(url=redirect_to,
                                               host=request.get_host()):

                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())
            if not redirect_to:
                redirect_to = reverse('dashboard')

            return redirect(redirect_to)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


@never_cache
def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    Moved here unaltered from django.contrib.auth.views only to apply the @never_cache decorator
    """
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return redirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': _('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)

    return render(request, template_name, context)


class Register(SessionWizardView):
    form_list = [
        ('register', RegistrationForm),
    ]

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        TEMPLATES = {
            'register': 'registration/register.html',
        }
        return [TEMPLATES[self.steps.current]]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            messages.error(
                self.request,
                "You attempted to access the registration form "
                "but you already have an account and are currently logged in."
            )
            return redirect(request.user.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def render(self, form=None, **kwargs):
        """
        Returns a ``HttpResponse`` containing all needed context data.
        """
        form = form or self.get_form()
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.

        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def process_approval(self, form):
        with transaction.atomic():
            data = self.request.POST.copy()
            if 'register-new_institution' in data:
                new_inst = Institution()
                new_inst.name = data['register-institution_name']
                new_inst.city = data['register-institution_city']
                new_inst.state = data['register-institution_state']
                new_inst.country = data['register-institution_country']
                new_inst.website = data['register-institution_website']
                new_inst.save()
            user = form.save(commit=False)
            user.is_active = False
            if 'register-new_institution' in data:
                user.institution = new_inst
            user.save()
            messages.success(self.request, PENDING_REGISTRATION_MESSAGE)
            # Email the contacts for this project
            subject = PENDING_APPROVAL_SUBJECT
            email_context = {
                'user': user,
                'site': get_current_site(self.request),
                'activation_key': self.get_activation_key(user),
            }
            template = 'emails/pending_registration'
            message = render_to_string('{}.txt'.format(template), email_context)
            html_message = render_to_string('{}.html'.format(template), email_context)
            mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL)
            mail.attach_alternative(html_message, 'text/html')
            mail.send()
            sync_user.send(sender=user.__class__, user=user)
        return redirect('/')

    def process_registration(self, form):
        with transaction.atomic():
            user = form.save()
            # This is not a proper view but a reusable function to remove duplication from views
            user = authenticate(email=user.email, password=form.cleaned_data['password1'])
            # We don't check `if user is not None` because if authenticate failed
            # we have bigger problems
            auth_login(self.request, user)
            messages.success(self.request, "Thank you for registering!")
            subject = REGISTRATION_SUCCESS_SUBJECT
            template = 'emails/registration_welcome'
            email_context = {
                'user': user,
            }
            send_transactional_mail(user.email, subject, template, email_context)
            sync_user.send(sender=user.__class__, user=user)
        return redirect('dashboard')

    def done(self, form_list, form_dict, **kwargs):
        form = form_dict['register']
        if form.cleaned_data['honeypot']:
            messages.error(
                self.request,
                "Authentication failed: you appear to be a bot.")
            return render(
                self.request,
                'registration/register.html',
                {
                    'form': form,
                },
            )
        if form.email_domain_matches():
            return self.process_registration(form)
        else:
            return self.process_approval(form)


class ActivationView(TemplateView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.
    """
    template_name = 'registration/activate.html'

    def get(self, *args, **kwargs):
        """
        The base activation logic; subclasses should leave this method
        alone and implement activate(), which is called from this
        method.

        """
        self.activate(*args, **kwargs)
        return redirect('/')

    def activate(self, *args, **kwargs):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        email = self.validate_key(kwargs.get('activation_key'))
        if email is not None:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(self.request, "No member was found with this email address: {}".format(email))
            else:
                if user.is_active:
                    messages.error(self.request, "{} has already been approved.".format(user.email))
                else:
                    user.is_active = True
                    user.save()
                    # Notify the user they can now login and complete their profile
                    subject = "Your account has been approved!"
                    template = 'emails/registration_approved'
                    context = {
                        'user': user,
                        'request': self.request,
                    }
                    send_transactional_mail(user.email, subject, template, context)
                    project = user.projectmembership_set.first().project
                    contact_email_addresses = project.get_contact_email_addresses()
                    admin_context = {
                        'site_prefix': settings.SITE_PREFIX.upper(),
                        'user': user,
                        'project': project,
                    }
                    for email in contact_email_addresses:
                        send_transactional_mail(
                            email,
                            '{} is now approved'.format(user.email),
                            'emails/registration_approved_admin',
                            admin_context
                        )
                    messages.success(self.request, "{} is now approved to complete their registration.".format(
                        user.email))
            # return so we don't accidentally pick up the following message.
            return
        messages.warning(self.request, "The link you followed is invalid.")

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or ``None`` if not.

        """
        try:
            email = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return email
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return None


def consolidate(inp, keyfunc, rollup_name):
    """ Rolls similar items in a list up under an array on the first i
        similar item.
        Given a keyfunc that looks at only the second and third column,
        Turns this:
             1 | a | b | c
             2 | d | e | f
             3 | d | e | g
             4 | d | h | i
        into
             1 | a | b | c | []
             2 | d | e | f | [3]   
             4 | d | h | i | []
         Item 3 rolled up into 2 because its key fields(d,e) were the same.
        """
    inp_len = len(inp)
    if inp_len < 2:
        return inp

    for i in range(inp_len - 1, 0, -1):
        elem = inp[i]
        ekey = keyfunc(elem)
        prev_elem = inp[i - 1]
        pekey = keyfunc(prev_elem)
        if ekey == pekey:
            # ensure the rollup name exists
            if not hasattr(prev_elem, rollup_name):
                setattr(prev_elem, rollup_name, [])
            # add elem to prev_elem
            getattr(prev_elem, rollup_name).append(elem)
            # and any of its rollups:
            if hasattr(elem, rollup_name):
                getattr(prev_elem, rollup_name).extend(
                    getattr(elem, rollup_name))
            # slice elem out of the input
            inp = inp[:i] + inp[i + 1:]
    return inp


@login_required
@never_cache
@page_template('actstream/_activity.html')
def dashboard(request, tab='activity', template_name='accounts/dashboard.html', extra_context=None):
    active_projects = request.user.active_projects()
    context = {
        'user': request.user,
        'edit': True,
        'tab': tab,
        'projects': active_projects,
    }
    request.session['last_viewed_path'] = request.get_full_path()
    # if user dashboard was viewed, prevent adding things to a group
    request.session['last_viewed_project'] = None
    activity_stream = Action.objects.filter(
        public=True
    )

    if tab == 'activity':
        project_ct = ContentType.objects.get_for_model(Project)
        user_ct = ContentType.objects.get_for_model(User)
        if not request.user.can_access_all_projects:
            activity_stream = request.user.get_activity_stream()

        if 'project' in request.GET or 'content_type' in request.GET or 'user_activity_only' in request.GET:
            filter_form = ProjectContentForm(request.GET, user=request.user)
            if filter_form.is_valid() and filter_form.cleaned_data.get(
                'content_type'):
                activity_stream = activity_stream.filter(
                    action_object_content_type=filter_form.cleaned_data[
                        'content_type'])

            if filter_form.is_valid() and filter_form.cleaned_data.get(
                'project'):
                project = filter_form.cleaned_data['project']
                activity_stream = activity_stream.filter(
                    target_content_type=project_ct,
                    target_object_id=project.id
                )

            if filter_form.is_valid() and filter_form.cleaned_data.get(
                'user_activity_only'):
                activity_stream = activity_stream.filter(
                    actor_content_type=user_ct,
                    actor_object_id=request.user.id
                )
        else:
            filter_form = ProjectContentForm(user=request.user)

        # consolidate duplicate entries ( they really differ by target only )
        activity_stream = consolidate(
            list(activity_stream),
            lambda a: str((a.actor_object_id,
                           a.verb,
                           a.action_object_content_type,
                           a.action_object_object_id)),
            'others')
        context.update({
            'activity_stream': activity_stream,
            'filter_form': filter_form,
        })
    elif tab == 'discussions':
        context['comment_list'] = sorted(
            request.user.get_bookmarked_content(ThreadedComment),
            key=lambda c: c.submit_date,
            reverse=True,
        )
        if request.is_ajax():
            template_name = 'comments/list.html'
    elif tab == 'casereports':
        reports = [r for r in request.user.get_bookmarked_content(CaseReport)
                   if r.workflow_state == WorkflowState.LIVE]
        from casereport.models import Physician
        try:
            phys = Physician.objects.filter(email=request.user.email)
            for phy in phys:
                reports += CaseReport.objects.filter(primary_physician=phy)
        except Physician.DoesNotExist:
            pass
        reps = {r for r in reports}
        context['case_reports'] = sorted(
            reps,
            key=lambda c: c.sort_date(),
            reverse=True,
        )
    elif tab == 'documents':
        docs = [doc for doc in request.user.get_bookmarked_content(Document)
                if doc is not None]
        context['documents'] = sorted(
            docs,
            key=lambda c: c.date_added,
            reverse=True,
        )
    elif tab == 'bibliography':
        refs = request.user.get_bookmarked_content(Reference)
        context['references'] = sorted(
            refs,
            key=lambda c: c.date_added,
            reverse=True,
        )

    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


@login_required
def profile(request, pk, template_name='accounts/profile.html', extra_context=None):
    user = get_object_or_404(User, pk=pk)
    institution = user.institution
    projects = user.active_projects()
    context = {
        'user': user,
        'institution': institution,
        'projects': projects,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


@login_required
@never_cache
def profile_edit(request, template_name='accounts/profile_edit.html'):
    if not request.user.can_access_all_projects:
        project_form = RestrictedProjectMembershipForm
    else:
        project_form = ProjectMembershipForm
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        data = request.POST.copy()

        if form.is_valid():
            if 'new_institution' in data:
                new_inst = Institution()
                new_inst.name = data['institution_name']
                new_inst.city = data['institution_city']
                new_inst.state = data['institution_state']
                new_inst.country = data['institution_country']
                new_inst.website = data['institution_website']
                new_inst.save()
                request.user.institution = new_inst
            form.save()
            messages.success(request, "Profile updated successfully")
            sync_user.send(sender=request.user.__class__, user=request.user)
            return redirect('dashboard')
        else:
            messages.error(request, MESSAGES_DEFAULT_FORM_ERROR)
    else:
        form = UserProfileForm(instance=request.user)
        if not request.user.bio:
            messages.info(request, "Please add your bio and any other details you'd like to share.")
    context = {
        'form': form,
    }
    return render(request, template_name, context)

