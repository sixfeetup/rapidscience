from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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
from django.views.generic import View

from el_pagination.decorators import page_template

from casereport.models import CaseReport
from rlp.accounts.models import User
from rlp.bibliography.models import ProjectReference
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document
from rlp.search.forms import ActionObjectForm
from .forms import InviteForm
from .models import Project
from .models import ProjectMembership
from .shortcuts import group_invite_choices


def projects_list(request, template_name="projects/projects_list.html"):
    context = {
        'projects': Project.objects.select_related('institution', 'topic')
    }
    return render(request, template_name, context)


@never_cache
@page_template('actstream/_activity.html')
def projects_detail(request, pk, slug, tab='activity', template_name="projects/projects_detail.html", extra_context=None):
    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    context = {
        'project': project,
        'projects': projects,
        'tab': tab,
    }
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
        activity_stream = project.get_activity_stream()
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
        documents = project.get_shared_content(Document)
        activity_stream = project.get_activity_stream(
            Document
        )
        if documents:
            activity_stream = activity_stream.exclude(action_object_object_id__in=[w.id for w in documents])
        context['activity_stream'] = activity_stream
        context['documents'] = documents
    elif tab == 'discussions':
        context['comment_list'] = project.get_shared_content(ThreadedComment)
        if request.is_ajax():
            template_name = 'comments/list.html'
        context['page_template'] = 'comments/list.html'
    elif tab == 'casereports':
        context['activity_stream'] = project.get_activity_stream(
            CaseReport
        )
        context['case_reports'] = project.get_shared_content(CaseReport)
    elif tab == 'bibliography':
        context['references'] = project.get_shared_content(ProjectReference)
        activity_stream = project.get_activity_stream(ProjectReference)
        context['activity_stream'] = activity_stream
    # member invite form
    invite_data = {
        'user': request.user.get_full_name(),
        'group': project.title,
        # TODO put a real invite link here
        'link': project.get_absolute_url(),
    }
    invite_msg = settings.GROUP_INVITATION_TEMPLATE.format(**invite_data)
    form = InviteForm(
        initial={'invitation_message': invite_msg},
    )
    form.fields['internal'].choices = group_invite_choices(project)
    context['form'] = form
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
        group = Project.objects.get(id=pk)
        form = InviteForm(request.POST)
        form.fields['internal'].choices = group_invite_choices(group)
        if form.is_valid():
            iu_ids = form.cleaned_data['internal']
            internal_addrs = User.objects.filter(
                id__in=iu_ids
            ).values_list('email', flat=True)
            external_addrs = form.cleaned_data['external']
            recipients = list(internal_addrs) + external_addrs
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
            return JsonResponse({
                'success': True,
                'message': '{} members invited'.format(len(recipients)),
            })
    return JsonResponse({
        'success': False,
        'message': 'Invitation failed',
    })

approval_tmpl = '''{} ({}) has requested access to the closed group “{}”.

A moderator for the group must approve this access. You can view and approve pending members on the group’s langing page:

{}
'''


class JoinGroup(LoginRequiredMixin, View):
    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)
        if request.user in project.users.all():
            message = (
                'You are already a member of the “{}” group, '
                'or your membership approval is pending'.format(project.title)
            )
            messages.error(request, message)
        elif project.approval_required:
            ProjectMembership.objects.create(
                user=request.user,
                project=project,
                state='pending',
            )
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
            # open group - add the user
            ProjectMembership.objects.create(
                user=request.user,
                project=project,
            )
            message = 'Welcome to the “{}” group'.format(
                project.title
            )
            messages.success(request, message)
            return redirect(project.get_absolute_url())
        return redirect(reverse('projects:projects_list'))
