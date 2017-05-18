from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import View, FormView, UpdateView

from el_pagination.decorators import page_template

from casereport.models import CaseReport
from rlp.accounts.models import User
from rlp.bibliography.models import Reference
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document
from rlp.search.forms import ActionObjectForm
from .forms import InviteForm, NewGroupForm, ModifyGroupForm
from .models import Project
from .models import ProjectMembership
from .shortcuts import group_invite_choices


@never_cache
def projects_list(request, template_name="projects/projects_list.html"):
    context = {
        'projects': Project.objects.select_related('institution', 'topic')
    }
    return render(request, template_name, context)


@login_required
@never_cache
@page_template('actstream/_activity.html')
def projects_detail(request, pk, slug, tab='activity', template_name="projects/projects_detail.html",
                    extra_context=None):
    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    context = {
        'project': project,
        'projects': projects,
        'tab': tab,
    }
    # URL to redirect to after content is posted
    request.session['last_viewed_path'] = request.get_full_path()
    request.session['last_viewed_object'] = ('project', project.id)
    # This must come first so we can override the ``page_template`` context variable
    if extra_context is not None:
        context.update(extra_context)
    # Hide closed group information from non-members
    if project.approval_required:
        if request.user.is_anonymous():
            return redirect(reverse('login'))
        if not request.user.can_access_project(project):
            raise PermissionDenied
    # determine if interaction will be allowed
    context['user_interaction'] = (
        hasattr(request.user, 'can_access_project') and
        request.user.can_access_project(project)
    )
    if tab == 'activity':
        activity_stream = project.get_activity_stream(user=request.user)
        if 'content_type' in request.GET:
            filter_form = ActionObjectForm(request.GET)
            if filter_form.is_valid() and filter_form.cleaned_data['content_type']:
                activity_stream = activity_stream.filter(
                    action_object_content_type=filter_form.cleaned_data['content_type'])
        else:
            filter_form = ActionObjectForm()
        context['activity_stream'] = activity_stream
        context['filter_form'] = filter_form
    elif tab == 'documents':
        context['documents'] = sorted(
            project.get_shared_content(Document),
            key=lambda c: c.date_added,
            reverse=True,
        )
    elif tab == 'discussions':
        context['comment_list'] = sorted(
            project.get_shared_content(ThreadedComment),
            key=lambda c: c.submit_date,
            reverse=True,
        )
        if request.is_ajax():
            template_name = 'comments/list.html'
        context['page_template'] = 'comments/list.html'
    elif tab == 'casereports':
        reports = project.get_shared_content(CaseReport)
        context['case_reports'] = sorted(
            (r.target for r in reports if r.target.workflow_state == 'live'),
            key=lambda c: c.sort_date(),
            reverse=True,
        )
    elif tab == 'bibliography':
        context['references'] = project.get_shared_content(Reference)
    # member invite form
    site = Site.objects.get_current()
    project_url = 'https://' + site.domain + project.get_absolute_url()
    invite_data = {
        'user': request.user.get_full_name(),
        'group': project.title,
        'link': project_url,
    }
    invite_msg = settings.GROUP_INVITATION_TEMPLATE.format(**invite_data)
    form = InviteForm(
        initial={'invitation_message': invite_msg},
    )
    form.fields['internal'].choices = group_invite_choices(project)
    context['form'] = form

    # inject the edit-form
    edit_form = ModifyGroupForm(initial=dict(
        group_id=project.id,
        group_name=project.title,
        approval=project.approval_required,
        banner_image=project.cover_photo,
    ))
    context['edit_group_form'] = edit_form

    # response
    return render(request, template_name, context)


@never_cache
@page_template('projects/_projects_members.html')
def projects_members(request, pk, slug, template_name='projects/projects_members.html', extra_context=None):
    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    context = {
        'project': project,
        'projects': projects,
        'memberships': project.projectmembership_set.filter(user__is_active=True).order_by('state', 'user__last_name')
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


def invite_members(request, pk, slug):
    if request.method == 'POST':
        if request.user.is_authenticated():
            group = Project.objects.get(id=pk)
            if not group.approval_required or ( request.user.is_superuser or request.user in group.moderators() ):
                form = InviteForm(request.POST)
                form.fields['internal'].choices = group_invite_choices(group)
                if form.is_valid():
                    internal_addrs = [
                        user.email for user in form.cleaned_data['internal']
                        ]
                    external_addrs = form.cleaned_data['external']
                    recipients = internal_addrs + external_addrs
                    subject = 'Invitation to join {}'.format(group.title)
                    message_data = (
                        (
                            subject,
                            form.cleaned_data['invitation_message'],
                            request.user.email,
                            [rcp],
                        )
                        for rcp in recipients
                    )
                    send_mass_mail(message_data)
                    messages.success(request, '{} members invited'.format(len(recipients)))
                    return redirect(request.META['HTTP_REFERER'])
    messages.error(request, 'Invitation failed')
    return redirect(request.META['HTTP_REFERER'])


approval_tmpl = '''{} ({}) has requested access to the closed group “{}”.

A moderator for the group must approve this access. You can view and approve pending members on the group’s langing page:

{}
'''


class LeaveGroup(LoginRequiredMixin, View):
    def get(self, request, pk, user):
        project = get_object_or_404(Project, id=pk)
        membership = get_object_or_404(ProjectMembership, project=project, user=user)
        user = get_object_or_404(User, id=user)
        if membership.state == 'moderator' and project.approval_required:
            message = 'Moderators cannot leave the groups that require moderation.'
            messages.error(request, message)
        elif membership.state == 'pending':
            membership.delete()
            message = 'Your pending application to the "{}" group has been canceled.'.format(project.title)
            messages.success(request, message)
        else:
            membership.delete()
            message = '{} has been removed from the "{}" group.'.format(user.get_full_name(), project.title)
            messages.success(request, message)

        return redirect(reverse('projects:projects_list'))


class JoinGroup(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)
        if request.user in project.users.all():
            message = (
                'You are already a member of the “{}” group, '
                'or your membership approval is pending'.format(project.title)
            )
            messages.error(request, message)
        else:
            membership = project.add_member(request.user)
            if membership.state == 'pending':
                send_mail(
                    'Request to join group “{}”'.format(project.title),
                    approval_tmpl.format(
                        request.user.get_full_name(),
                        request.user.email,
                        project.title,
                        request.build_absolute_uri(reverse(
                            'projects:projects_detail',
                            kwargs={
                                'pk': project.id,
                                'slug': slugify(project.title),
                            },
                        )),
                    ),
                    request.user.email,
                    project.get_contact_email_addresses(),
                )
                message = ('“{}” is a closed group. The moderators have been '
                           'asked to review your request to '
                           'join.'.format(project.title))
                messages.success(request, message)
            else:
                message = 'Welcome to the “{}” group'.format(
                    project.title
                )
                messages.success(request, message)
                return redirect(project.get_absolute_url())
        return redirect(reverse('projects:projects_list'))


class AddGroup(LoginRequiredMixin, FormView):
    form_class = NewGroupForm
    template_name = 'projects/projects_add.html'

    def get_form(self, form_class):
        # super.get_form() handles POST data if available
        form = super(AddGroup, self).get_form(form_class)
        invite_choices = (
            (user.id, user.get_full_name())
            for user in User.objects.all()
            if user != self.request.user
        )
        form.fields['internal'].choices = invite_choices
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, "Please correct the errors below")
            return self.form_invalid(form)

    def form_valid(self, form):
        data = form.cleaned_data
        user = self.request.user
        new_group = Project(
            title=data['group_name'],
            goal=data['about'],
            approval_required=int(data['approval']),
            slug=slugify(data['group_name']),
        )
        if 'banner_image' in self.request.FILES.keys():
            new_group.cover_photo = self.request.FILES['banner_image']
        new_group.save()
        ProjectMembership.objects.create(
            user=user,
            project=new_group,
            state='moderator',
        )
        new_group.invite_registered_users(form.cleaned_data['internal'])
        new_group.invite_external_emails(form.cleaned_data['external'])
        return redirect(new_group.get_absolute_url())


class EditGroup(LoginRequiredMixin, FormView):
    form_class = ModifyGroupForm
    template_name = 'projects/projects_edit.html'  # re-using

    def get(self, request, pk, slug):
        project = get_object_or_404(Project, id=pk)
        if request.user not in project.moderators():
            message = (
                'You are not a moderator of the “{}” group, '.format(project.title)
            )
            messages.error(request, message)
            return redirect(project.get_absolute_url())
        else:
            form = self.form_class(initial=dict(
                group_id=project.id,
                group_name=project.title,
                about=project.goal,
                approval=1 if project.approval_required else 0,
                banner_image=project.cover_photo.url if project.cover_photo else None,
            ))
        return self.render_to_response(self.get_context_data(form=form, project=project), )

    def post(self, request, *args, **kwargs):
        """ Handle the POSTed form data.
            This overrides the FormView impl only to add the messages.error call
        """
        project = get_object_or_404(Project, id=kwargs['pk'])
        form = self.get_form()
        if form.is_valid():
            res = self.form_valid(form)
            messages.info(request, "Edits saved!")

            # internal invites
            new_invitees = [invitee for invitee in form.cleaned_data['internal'] if
                            invitee not in project.active_members()]
            project.invite_registered_users(new_invitees)

            # external invites
            # TODO: if the email matches an internal user, upgrade the invite
            project.invite_external_emails(form.cleaned_data['external'])

            messages.info(request, "Invites Sent!")

            return res

        else:
            messages.error(request, "Please correct the errors below")
            return self.render_to_response(self.get_context_data(form=form, project=project), )  # we can't do this because we were in an overlay on another page
            # This really should be a rest POST and return a json success/error message

    def form_valid(self, form):
        """ Update the Project and send any new invites.
            Won't send invites to those who are already members.
        """
        data = form.cleaned_data
        # update the Project
        project = Project.objects.get(pk=data['group_id'])
        project.title = data['group_name']
        project.goal = data['about']
        if data['banner_image']:
            fcontent = self.request.FILES['banner_image']
            fname = fcontent.name
            project.cover_photo.save(fname, fcontent)

        project.save()

        return redirect(project.get_absolute_url())
