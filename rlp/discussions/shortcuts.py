from django.contrib.contenttypes.models import ContentType

from .models import ThreadedComment


def get_comments_for_instance(instance):
    content_type = ContentType.objects.get_for_model(instance.__class__)
    qs = ThreadedComment.objects.filter(content_type=content_type, object_pk=instance.id)
    return qs


def get_url_for_comment(object):
    """Returns the detail view of the top-level target of the comment thread."""
    # If this is a comment, get the top level comment
    comment_id = None
    if hasattr(object, 'level'):
        comment_id = object.id  # TODO: add anchor fragment to url
        while object.level:
            object = object.content_object
    content_type = ContentType.objects.get_for_model(object.__class__)
    if content_type.model == 'threadedcomment':
        # This is a top-level comment, so pick it's content_object
        object = object.content_object
    target_ct = ContentType.objects.get_for_model(object.__class__)
    if target_ct.model == 'project':
        return object.get_discussions_url()
    elif target_ct.model == 'bibliography':
        # TODO reverse the url for the bibliography tab, this item is a bibliographic reference, not a project
        return ""
    return object.get_absolute_url()
