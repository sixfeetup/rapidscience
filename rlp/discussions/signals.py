from django.conf import settings
from django.contrib import messages
from django.dispatch import receiver

from actstream import action
from django_comments.signals import comment_was_posted

from casereport.models import CaseReportReview
from rlp.accounts.models import User
from rlp.projects.models import Project


@receiver(comment_was_posted)
def create_comment_activity(**kwargs):
    request = kwargs['request']
    # Add the message here since the django-contrib-comments
    # view doesn't add a message.
    messages.success(request, "Your comment was added!")
    comment = kwargs['comment']
    # Don't create an action item for duplicate comments.
    # django-contrib-comments will detect duplicates and return the original
    # comment, so we have to guard against accidentally adding duplicate
    # entries to the activity stream.
    if comment.action_object_actions.count():
        return
    if comment.is_reply:
        verb = 'reply'
    else:
        verb = 'comment'

    is_public = True

    # find the object being commented on
    top_comment = comment.discussion_root
    if top_comment.is_discussion:
        # unshared discussion activity is kept private
        # this presumes we are sharing discussion roots and not individual items
        if len(top_comment.get_viewers() - {comment.user}) == 0:
            is_public = False
        content = top_comment
    else:
        content = top_comment.content_object

    # automatically bookmark when commenting
    if hasattr(content, 'is_bookmarked_to'):
        if not content.is_bookmarked_to(comment.user):
            comment.user.bookmark(content)

        last_proj = request.session.get('last_viewed_project')
        if last_proj:
            group = Project.objects.get(id=last_proj)
            if not content.is_bookmarked_to(group):
                group.bookmark(content)

    # per #746   a comment by an admin on a CaseReportReview, we need to set
    # the target to the CRR's casereport author
    action_kwargs = {
        'verb': verb,
        'action_object': comment,
        'public': is_public,
    }
    send_to_viewers = True
    if comment.user.is_staff and comment.is_editorial_note:
        casereport = top_comment.content_object.casereport
        author = User.objects.filter(
            email__iexact=casereport.primary_author.email
        ).first()
        action_kwargs['target'] = author
        # this is notice from an admin to a user,
        # so do not propagate the message if there are pending shares
        send_to_viewers = False
    new_action = action.send(comment.user, **action_kwargs)


    if send_to_viewers and hasattr(content, 'share_with'):
        content.notify_viewers(
            '{}: A new comment was posted'.format(
                settings.SITE_PREFIX.upper(),
            ),
            {'action': new_action[0][1]},
        )

        # add it to the AF of the others
        for interested_party in content.get_viewers() - {request.user}:
            action.send( comment.user,
                         verb=verb,
                         action_object=comment,
                         target=interested_party)
