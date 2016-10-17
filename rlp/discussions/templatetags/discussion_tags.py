from django.contrib.contenttypes.models import ContentType
from django import template
from django.template.loader import render_to_string

from django_comments.templatetags.comments import BaseCommentNode

from rlp.discussions.forms import ThreadedCommentForm
from rlp.discussions.models import ThreadedComment
from rlp.discussions.shortcuts import get_url_for_comment

register = template.Library()


@register.simple_tag(takes_context=True)
def get_reply_form(context, comment):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_reply_form comment %}
    """
    request = context['request']
    form = ThreadedCommentForm(comment, comment=comment)
    ctype = ContentType.objects.get_for_model(comment)
    template_search_list = [
        "comments/%s/%s/form.html" % (ctype.app_label, ctype.model),
        "comments/%s/form.html" % ctype.app_label,
        "comments/form.html"
    ]
    context_dict = {
        'form': form,
        'button_label': 'Reply',
    }
    return render_to_string(template_search_list, context_dict, request=request)


@register.assignment_tag
def get_next_for_comment(object):
    return get_url_for_comment(object)


class CommentCountNode(BaseCommentNode):
    """Insert a count of comments into the context."""

    def get_context_value_from_queryset(self, context, qs):
        count = qs.count()
        if not count:
            return 0
        ids = set(qs.values_list('id', flat=True))
        current_level_ids = set(qs.values_list('id', flat=True))
        next_level = ThreadedComment.objects.filter(parent_id__in=current_level_ids).exclude(id__in=ids)
        while next_level.count():
            count += next_level.count()
            ids.update(next_level.values_list('id', flat=True))
            current_level_ids = set(next_level.values_list('id', flat=True))
            next_level = ThreadedComment.objects.filter(parent_id__in=current_level_ids).exclude(id__in=ids)
        assert count == len(ids)
        return count


@register.tag
def get_threaded_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_threaded_comment_count for [object] as [varname]  %}
        {% get_threaded_comment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_threaded_comment_count for event as comment_count %}
        {% get_threaded_comment_count for calendar.event event.id as comment_count %}
        {% get_threaded_comment_count for calendar.event 17 as comment_count %}

    """
    return CommentCountNode.handle_token(parser, token)
