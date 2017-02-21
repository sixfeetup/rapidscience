from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from actstream.models import Action
from el_pagination.decorators import page_template

from casereport.models import CaseReport
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document
from rlp.search.forms import ActionObjectForm
from .models import Project


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
    project_ct = ContentType.objects.get_for_model(Project)
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
        working_documents = [
            doc for doc in project.get_shared_content(Document)
            if doc.working_document
        ]
        activity_stream = project.get_activity_stream(
            Document
        )
        if working_documents:
            activity_stream = activity_stream.exclude(action_object_object_id__in=[w.id for w in working_documents])
        context['activity_stream'] = activity_stream
        context['working_documents'] = working_documents
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
        activity_stream = Action.objects.filter(
            action_object_content_type=ContentType.objects.get(app_label='bibliography', model='projectreference'),
            target_object_id=project.id, target_content_type=project_ct
        )
        context['activity_stream'] = activity_stream
    return render(request, template_name, context)


@never_cache
@page_template('projects/_projects_members.html')
def projects_members(request, pk, slug, template_name='projects/projects_members.html', extra_context=None):
    projects = Project.objects.select_related('institution', 'topic')
    project = get_object_or_404(projects, pk=pk, slug=slug)
    context = {
        'project': project,
        'projects': projects,
        'memberships': project.projectmembership_set.filter(user__is_active=True).order_by('role__order', 'user__last_name')
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)
