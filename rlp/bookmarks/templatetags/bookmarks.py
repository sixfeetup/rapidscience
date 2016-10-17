from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def has_bookmark_permission(context, action):
    """Checks if the current user can bookmark the action item.
    Returns a boolean.

    Syntax::

        {% has_bookmark_permission action %}
    """
    request = context['request']
    if not request.user.is_authenticated():
        return False
    existing_bookmark = request.user.bookmark_set.filter(
        object_pk=action.action_object.pk, content_type=action.action_object_content_type
    ).count()
    has_permission = True
    if action.target.approval_required and not request.user.can_access_all_projects:
        has_permission = False
    if existing_bookmark or not has_permission:
        return False
    return True
