from django.conf import settings
from django.contrib import messages
from django.dispatch import receiver

from actstream import action
from django_comments.signals import comment_was_posted


@receiver(comment_was_posted)
def create_comment_activity(**kwargs):
    from .models import ThreadedComment
    request = kwargs['request']
    # Add the message here since the django-contrib-comments view doesn't add a message.
    messages.success(request, "Your comment was added!")
    comment = kwargs['comment']
    # Don't create an action item for duplicate comments. django-contrib-comments will detect duplicates and return the
    # original comment, so we have to guard against accidentally adding duplicate entries to the activity stream.
    if comment.action_object_actions.count():
        return
    viewer = comment.content_object
    if comment.is_reply():
        verb = 'reply'
    else:
        verb = 'comment'
    new_action = action.send(comment.user, verb=verb, action_object=comment, target=viewer)
    # TODO get a list of all viewers
    # for viewer in everyone_sharing_this:
    #     viewer.notify_members(
    #         '{}: A new comment was posted'.format(
    #             settings.SITE_PREFIX.upper()
    #         ),
    #         {'action': new_action[0][1]},
    #     )
