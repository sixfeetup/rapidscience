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

from casereport.models import CaseReport
from rlp.bibliography.models import fetch_publications_for_user
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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            project_membership = ProjectMembership.objects.create(user=user,
                                                                  project=form.cleaned_data['project'],
                                                                  role=form.cleaned_data['role'])
            # Automatically add user to 'auto opt-in' projects if applicable
            for project in Project.objects.filter(auto_opt_in=True).exclude(pk=form.cleaned_data['project'].pk):
                ProjectMembership.objects.create(user=user, project=project)
            messages.success(self.request, PENDING_REGISTRATION_MESSAGE)
            # Email the contacts for this project
            contact_email_addresses = project_membership.project.get_contact_email_addresses()
            subject = PENDING_APPROVAL_SUBJECT
            email_context = {
                'user': user,
                'project': project_membership.project,
                'site': get_current_site(self.request),
                'activation_key': self.get_activation_key(user),
            }
            template = 'emails/pending_registration'
            message = render_to_string('{}.txt'.format(template), email_context)
            html_message = render_to_string('{}.html'.format(template), email_context)
            mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, contact_email_addresses)
            mail.attach_alternative(html_message, 'text/html')
            mail.send()
            sync_user.send(sender=user.__class__, user=user)
        return redirect('/')

    def process_registration(self, form):
        with transaction.atomic():
            user = form.save()
            ProjectMembership.objects.create(user=user,
                                             project=form.cleaned_data['project'],
                                             role=form.cleaned_data['role'])
            # Automatically add user to 'auto opt-in' projects if applicable
            for project in Project.objects.filter(auto_opt_in=True).exclude(pk=form.cleaned_data['project'].pk):
                ProjectMembership.objects.create(user=user, project=project)
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
        if form.cleaned_data['project'].approval_required:
            return self.process_approval(form)
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


@login_required
@never_cache
@page_template('actstream/_activity.html')
def dashboard(request, tab='activity', template_name='accounts/dashboard.html', extra_context=None):
    context = {
        'user': request.user,
        'edit': True,
        'tab': tab,
    }
    activity_stream = Action.objects.filter(
        public=True
    )
    if tab == 'activity':
        from rlp.projects.models import Project
        project_ct = ContentType.objects.get_for_model(Project)
        if not request.user.can_access_all_projects:
            activity_stream = activity_stream.filter(
                target_content_type=project_ct,
                target_object_id__in=list(Project.objects.filter(approval_required=False).values_list('id', flat=True))
            )
        if 'project' in request.GET or 'content_type' in request.GET or 'user_activity_only' in request.GET:
            filter_form = ProjectContentForm(request.GET, user=request.user)
            if filter_form.is_valid() and filter_form.cleaned_data.get('content_type'):
                activity_stream = activity_stream.filter(
                    action_object_content_type=filter_form.cleaned_data['content_type'])
            if filter_form.is_valid() and filter_form.cleaned_data.get('project'):
                project = filter_form.cleaned_data['project']
                activity_stream = activity_stream.filter(
                    target_content_type=project_ct,
                    target_object_id=project.id
                )
            if filter_form.is_valid() and filter_form.cleaned_data.get('user_activity_only'):
                user_ct = ContentType.objects.get_for_model(User)
                activity_stream = activity_stream.filter(
                    actor_content_type=user_ct,
                    actor_object_id=request.user.id
                )
        else:
            filter_form = ProjectContentForm(user=request.user)
        context.update({
            'activity_stream': activity_stream,
            'filter_form': filter_form,
        })
    elif tab == 'discussions':
        context['comment_list'] = request.user.get_shared_content(
            ThreadedComment
        )
        # TODO discussions aren't showing on the page
        if request.is_ajax():
            template_name = 'comments/list.html'
        context['activity_stream'] = []
    elif tab == 'casereports':
        context['activity_stream'] = []
        context['case_reports'] = request.user.get_shared_content(CaseReport)
    elif tab == 'documents':
        context['activity_stream'] = []
        context['working_documents'] = request.user.get_shared_content(Document)
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


@never_cache
@page_template('actstream/_activity.html')
def profile(request, pk, tab='activity', template_name='accounts/profile.html', extra_context=None):
    user = get_object_or_404(User, pk=pk)
    user_ct = ContentType.objects.get_for_model(User)
    context = {
        'user': user,
        'tab': tab,
    }
    if request.user.is_anonymous() or tab == 'publications':
        if user.orcid:
            if not user.publication_set.count():
                fetch_publications_for_user(user)
            context['publications'] = user.publication_set.all()
    # Bail early for the public view
    if request.user.is_anonymous():
        return render(request, 'accounts/profile_public.html', context)
    activity_stream = Action.objects.filter(
        actor_object_id=user.id, actor_content_type=user_ct
    )
    if tab == 'activity':
        if not request.user.can_access_all_projects:
            # Filter activity_stream
            from rlp.projects.models import Project
            activity_stream = activity_stream.filter(
                target_content_type=ContentType.objects.get_for_model(Project),
                target_object_id__in=list(Project.objects.filter(approval_required=False).values_list('id', flat=True))
            )
        if 'content_type' in request.GET:
            filter_form = ActionObjectForm(request.GET)
            if filter_form.is_valid() and filter_form.cleaned_data['content_type']:
                activity_stream = activity_stream.filter(
                    action_object_content_type=filter_form.cleaned_data['content_type'])
        else:
            filter_form = ActionObjectForm()
        context['activity_stream'] = activity_stream
        context['filter_form'] = filter_form
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
    ProjectFormset = inlineformset_factory(
        User, ProjectMembership,
        form=project_form,
        fields=('project', 'role')
    )
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        formset = ProjectFormset(
            request.POST,
            instance=request.user,
            queryset=request.user.projectmembership_set.exclude(project__auto_opt_in=True)
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Profile updated successfully")
            sync_user.send(sender=request.user.__class__, user=request.user)
            return redirect('dashboard')
        else:
            messages.error(request, MESSAGES_DEFAULT_FORM_ERROR)
    else:
        form = UserProfileForm(instance=request.user)
        formset = ProjectFormset(
            instance=request.user,
            queryset=request.user.projectmembership_set.exclude(project__auto_opt_in=True)
        )
        if not request.user.bio:
            messages.info(request, "Please add your bio and any other details you'd like to share.")
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, template_name, context)

