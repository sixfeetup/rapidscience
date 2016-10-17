from django import template

from rlp.projects.models import Project, Topic

register = template.Library()


@register.inclusion_tag(
    'projects/_projects.html',
    takes_context=True
)
def projects_sidebar(context):
    context['top_level_projects'] = Project.objects.filter(topic__isnull=True)
    context['topics'] = Topic.objects.all()
    return context


@register.inclusion_tag(
    'projects/_members.html',
)
def show_project_members(project):
    return {
        'project': project,
        'memberships': project.projectmembership_set.filter(
            user__is_active=True).order_by('role__order', 'user__first_name')
    }

