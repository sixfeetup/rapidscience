from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.views.generic import View, FormView

from el_pagination.decorators import page_template

from casereport.constants import WorkflowState
from casereport.models import CaseReport
from rlp.accounts.models import User
from rlp.core.utils import rollup, resolve_email_targets
from rlp.bibliography.models import Reference, UserReference
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document
from rlp.search.forms import ProjectContentForm, get_action_object_content_types
from rlp.projects import emails
from .forms import InviteForm, NewGroupForm, ModifyGroupForm, EditGroupNotifications
from .models import Project
from .models import ProjectMembership
from .shortcuts import group_invite_choices

from actstream import action


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
    # if tab == 'undefined':
    #     raise ValueError('better call anthony')

    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    context = {
        'project': project,
        'projects': projects,
        'tab': tab,
        'content_types': get_action_object_content_types()
    }
    # URL to redirect to after content is posted
    request.session['last_viewed_path'] = request.get_full_path()
    request.session['last_viewed_project'] = project.id
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
    if 'content_type' in request.GET or 'user_activity_only' in request.GET:
        user_ct = ContentType.objects.get_for_model(User)
        filter_form = ProjectContentForm(request.GET, user=request.user)
    else:
        filter_form = ProjectContentForm(user=request.user)
    context['filter_form'] = filter_form
    if tab == 'activity':
        print("project activity")
        activity_stream = project.get_activity_stream(user=request.user)
        if filter_form.is_valid() and filter_form.cleaned_data['content_type']:
            activity_stream = activity_stream.filter(
                action_object_content_type=filter_form.cleaned_data[
                    'content_type'])
        if filter_form.is_valid() and filter_form.cleaned_data.get(
            'user_activity_only'):
            activity_stream = activity_stream.filter(
                actor_content_type=user_ct,
                actor_object_id=request.user.id
            )
        print("consolidating")
        activity_stream = list(rollup(activity_stream, 'all_targets',
                                      rollup_attr='target'))

        context['activity_stream'] = activity_stream
    elif tab == 'documents':
        docs = [doc for doc in project.get_bookmarked_content(Document)
                if doc is not None]
        if filter_form.is_valid() and filter_form.cleaned_data.get(
                'user_activity_only'):
            docs = [doc for doc in docs
                    if doc.owner.id == request.user.id]
        context['documents'] = sorted(
            docs,
            key=lambda c: c.date_added,
            reverse=True,
        )
    elif tab == 'discussions':
        comments = sorted(
            project.get_bookmarked_content(ThreadedComment),
            key=lambda c: c.submit_date,
            reverse=True,
        )
        if filter_form.is_valid() and filter_form.cleaned_data.get(
                'user_activity_only'):
            comments = [comment for comment in comments
                        if comment.user and comment.user.id == request.user.id]
        context['comment_list'] = comments
        if request.is_ajax():
            template_name = 'comments/list.html'
        context['page_template'] = 'comments/list.html'
    elif tab == 'casereports':
        # only show CRs shared with the current group
        # show all CRs created by the user, regardless of state
        # only show live CRs that were not created by the user
        reports = [r for r in project.get_bookmarked_content(CaseReport)]
        display_cr = []
        user_only = filter_form.is_valid() and filter_form.cleaned_data.get('user_activity_only')
        for r in reports:
            if user_only and r.primary_author == request.user:
                display_cr.append(r)
                continue
            elif user_only and not r.primary_author == request.user:
                continue
            if r.primary_author == request.user:
                display_cr.append(r)
            elif r.workflow_state == WorkflowState.LIVE:
                display_cr.append(r)
        context['case_reports'] = sorted(
            display_cr,
            key=lambda c: c.sort_date(),
            reverse=True,
        )
    elif tab == 'bibliography':
        refs = project.get_bookmarked_content(UserReference)
        if filter_form.is_valid() and filter_form.cleaned_data.get(
                'user_activity_only'):
            refs = [ref for ref in refs
                    if ref.user.id == request.user.id]
        context['references'] = sorted(
            refs,
            key=lambda c: c.date_updated,
            reverse=True,
        )
    form = InviteForm()

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

    if request.user in project.active_members():
        email_prefs_form = EditGroupNotifications.get_form_for_user_and_group(request.user, project)
        context['edit_group_email_prefs_form'] = email_prefs_form

    # response
    return render(request, template_name, context)


@never_cache
@page_template('projects/_projects_members.html')
def projects_members(request, pk, slug, template_name='projects/projects_members.html', extra_context=None):
    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    # members list differs by viewer
    if request.user.is_staff or request.user in project.moderators.all():
        memberships = project.projectmembership_set.filter(user__is_active=True).exclude(state='ignored')
    else:
        memberships = project.projectmembership_set.filter(user__is_active=True,
                                                           state__in=('member', 'moderator'))

    memberships = memberships.order_by('state', 'user__last_name')
    context = {
        'project': project,
        'projects': projects,
        'memberships': project.projectmembership_set.filter(user__is_active=True).order_by('state', 'user__last_name')
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)


def invite_members(request, pk, slug):
    if request.method != 'POST' or not request.user.is_authenticated():
        messages.error(request, 'Invitation failed')
        return redirect(request.META['HTTP_REFERER'])
    group = Project.objects.get(id=pk)
    if not group.approval_required or (request.user.is_superuser or request.user in group.moderators()):
        form = InviteForm(request.POST)
        form.fields['internal'].choices = group_invite_choices(group)
        if form.is_valid():
            message = form.cleaned_data['invitation_message']

            internal_users = form.cleaned_data['internal']

            internal_addrs = resolve_email_targets(internal_users, force=True)
            external_addrs = resolve_email_targets(form.cleaned_data['external'],
                                                   exclude=internal_users,
                                                   force=True)

            # Non-members - create user and send specific registration link
            emails.project_invite_nonmember(request, external_addrs, group, message)

            # site members
            emails.project_invite_member(request, internal_addrs, group, message)

            # message the results back
            if not group.approval_required:
                for invitee in User.objects.filter(id__in=internal_users):
                    action.send(request.user, verb='invited', action_object=group, target= invitee, description=message)
            recipients = internal_addrs.union(external_addrs)
            count = len(recipients)
            messages.success(request, '{} member{} invited'.format(
                count, count > 1 and 's' or ''))
            return redirect(request.META['HTTP_REFERER'])
    messages.error(request, 'Invitation failed')
    return redirect(request.META['HTTP_REFERER'])


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
                emails.join_request_to_mods(request, project)
                message = ('Your request has been sent to ' +
                           'the moderator of this group.')
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

    def get_form(self, form_class=NewGroupForm):
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
            return self.form_valid(form, request)
        else:
            messages.error(request, "Please correct the errors below")
            return self.form_invalid(form)

    def form_valid(self, form, request):
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
        internal_users = form.cleaned_data['internal']
        internal_addrs = resolve_email_targets(internal_users, force=True)
        message = form.cleaned_data['invitation_message']
        emails.project_invite_member(request, internal_addrs, new_group,
                                     message)

        external_addrs = resolve_email_targets(form.cleaned_data['external'],
                                               exclude=internal_users,
                                               force=True)
        emails.project_invite_nonmember(request, external_addrs, new_group,
                                        message)
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
        invite_choices = (
            (user.id, user.get_full_name())
            for user in User.objects.all()
            if user != self.request.user and project not in user.projects.all()
        )
        form.fields['internal'].choices = invite_choices
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

            message = form.cleaned_data['invitation_message']

            internal_users = [member for member in form.cleaned_data['internal']
                              if member not in project.active_members()]
            internal_addrs = resolve_email_targets(internal_users, force=True)
            emails.project_invite_member(request, internal_addrs, project, message)

            external_addrs = resolve_email_targets(form.cleaned_data['external'],
                                                   exclude=project.active_members(),
                                                   force=True)
            emails.project_invite_nonmember(request, external_addrs, project, message)

            if internal_addrs or external_addrs:
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


class PromoteToModerator(LoginRequiredMixin, View):
    def get(self, request, membership_id):
        membership = get_object_or_404(ProjectMembership, id=membership_id)
        group = membership.project
        if membership.state in ('member',):
            if request.user.is_staff or request.user in group.moderators():
                membership.promote()
                membership.save()
        return redirect(group.get_absolute_url())


class DemoteToMember(LoginRequiredMixin, View):
    def get(self, request, membership_id):
        membership = get_object_or_404(ProjectMembership, id=membership_id)
        group = membership.project
        if membership.state in ('moderator',):
            if request.user.is_staff or request.user in group.moderators():
                membership.demote()
                membership.save()
        return redirect(group.get_absolute_url())


class AcceptMembershipRequest(LoginRequiredMixin, View):
    def get(self, request, membership_id):
        membership = get_object_or_404(ProjectMembership, id=membership_id)
        group = membership.project

        if membership.state in ('pending', 'ignored'):
            if request.user.is_staff or request.user in group.moderators():
                membership.approve()
                membership.save()
                emails.approve_to_requester(request, membership, group)
        return redirect(group.get_absolute_url())


class IgnoreMembershipRequest(LoginRequiredMixin, View):
    def get(self, request, membership_id):
        membership = get_object_or_404(ProjectMembership, id=membership_id)
        group = membership.project

        if membership.state in ('pending', 'ignored'):
            if request.user.is_staff or request.user in group.moderators():
                membership.ignore()
                membership.save()
                emails.reject_to_requester(request, membership, group)
        return redirect(group.get_absolute_url())


class EditGroupNotificationsView(LoginRequiredMixin, FormView):
    form_class = EditGroupNotifications
    # template_name=

    def post(self, request):
        user = request.user
        group_id = int(request.POST.get('group_id'))
        group = Project.objects.get(id=group_id)
        form = self.get_form()
        membership = ProjectMembership.objects.get(user=user, project=group)
        pref = request.POST.get('group_prefs')

        if pref == 'immediately':
            membership.email_prefs = 'user_and_group'
            membership.digest_prefs = 'disabled'

        elif pref == 'weekly':
            membership.email_prefs = 'disabled'
            membership.digest_prefs = 'enabled'

        elif pref == 'both':
            membership.email_prefs = 'user_and_group'
            membership.digest_prefs = 'enabled'

        elif pref == 'never':
            membership.email_prefs = 'disabled'
            membership.digest_prefs = 'disabled'

        elif pref == 'none':
            membership.email_prefs = None
            membership.digest_prefs = None

        else:
            from rlp import logger
            logger.error("unexpected group email prefs values:{}".format(pref))
        membership.save()
        return JsonResponse({'message':'success'})
