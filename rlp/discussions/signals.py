from django.conf import settings
from django.contrib import messages
from django.dispatch import receiver

from actstream import action
from django_comments.signals import comment_was_posted

from rlp.accounts.models import User
from rlp.core.email import send_transactional_mail, activity_mail
from rlp.projects.models import Project

from django.core.urlresolvers import reverse


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
        if last_proj and last_proj != -1:
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
        # add it to the AF of the others
        interested_parties = content.get_viewers() - {request.user}
        if top_comment.user != request.user and \
                top_comment.user not in content.get_viewers():
            interested_parties.add( top_comment.user)

        # and add the authors of the content object
        if hasattr(content, "primary_author"):
            interested_parties.add( content.primary_author)
        if hasattr(content, "co_author"):
            # it should have been plural?
            for ca in content.co_author.all():
                interested_parties.add(ca)
        if hasattr(content, "user"):
            interested_parties.add( content.user)
        if hasattr(content,"owner"):
            interested_parties.add( content.owner)

        for interested_party in interested_parties:
            action.send( comment.user,
                         verb=verb,
                         action_object=comment,
                         target=interested_party)

        activity_mail(comment.user, comment, content.get_viewers(), request)
    if content.__class__.__name__=='CaseReport':
        # disc_root = obj.discussion_root
        # root_obj = disc_root.content_object
        user_url = request.build_absolute_uri(
            reverse('profile', kwargs={'pk': request.user.pk}))
        author = content.casereport.primary_author
        author_link = request and request.build_absolute_uri(
            reverse('profile',
                    kwargs={'pk': author.id})) \
                      or "https://" + settings.DOMAIN + \
                         author.get_absolute_url()
        cr_link = "https://" + settings.DOMAIN + content.casereport.get_absolute_url()
        mail_data = {
            'user': request.user.get_full_name(),
            'user_link': user_url,
            'casereport': content.casereport,
            'title': content.casereport.title,
            'link': cr_link,
            'comment': comment.comment,
            'author': content.casereport.primary_author.get_full_name,
            'author_link': author_link
        }
        for admin in User.objects.filter(is_staff=True):
            send_transactional_mail(
            admin.email,
            'Member comment on case report',
            'emails/comment_admin',
            mail_data,
            "Cases Central <edit@rapidscience.org>"
            )

@receiver(comment_was_posted)
def review_notification(**kwargs):
    '''notify case report author when a review comment is posted'''
    comment = kwargs['comment']
    if not comment.user.is_staff:
        return
    if not comment.is_editorial_note:
        return
    review = comment.content_object
    author = review.casereport.primary_author
    site_url = "https://" + settings.DOMAIN

    mail_data = {
        'user': author,
        'casereport': review.casereport,
        'comment': comment.comment,
        'site_url': site_url,
    }
    send_transactional_mail(
        author.email,
        'Editorial comment regarding your case report',
        'emails/review',
        mail_data,
        "Cases Central <edit@rapidscience.org>"
    )
