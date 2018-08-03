import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from rlp import logger
from rlp.accounts.models import User
from rlp.core.utils import resolve_email_targets
from .models import EmailLog


def send_transactional_mail(to_email, subject, template, context, from_email=settings.DEFAULT_FROM_EMAIL):
    """Shortcut for sending transactional emails (both html and plain text) to a
    single recipient.
    ``template`` should be the file name without the file extension e.g. 'emails/test'
    rather than 'emails/test.html'.
    """
    context['site'] = Site.objects.get_current()
    message = render_to_string(template + '.txt', context)
    html_message = render_to_string(template + '.html', context)
    email_log = EmailLog.objects.create(
        subject=subject, to_email=to_email, message_html=html_message, message_text=message)
    # WARNING: SMTP headers cannot be longer than 72 characters. We should be ok for now with just the pk of EmailLog
    # but should switch to using their official library so it is line wrapped automatically.
    headers = {'X-SMTPAPI': json.dumps({'EmailLogId': str(email_log.id)})}
    mail = EmailMultiAlternatives(subject, message, from_email, [to_email], headers=headers)
    mail.attach_alternative(html_message, 'text/html')
    return mail.send()


def activity_mail(user, obj, target, request=None):
    """ send an activity style email ( shared, commented, etc ) relating
        user to obj, to everyone in target.
        Target can a user, a email address string, a group, or a list
        comprised of all three types.
        Groups(projects) are broken down into users.
        Users who have opted out of receiving emails are removed from the
        set.
    """
    if target == user:
        return
    if not target:
        logger.warn("activity_mail called with no targets!")
        return

    context = {}
    comment = ""
    link = "https://" + settings.DOMAIN + obj.get_absolute_url()
    template = 'core/emails/activity_email'

    recipients = resolve_email_targets(target, exclude=user)

    cls_name = obj.__class__.__name__
    root_obj_cls_name = cls_name

    try:
        title = obj.title
    except AttributeError:
        title = ''
    if cls_name == 'UserReference':
        from rlp.bibliography.models import Reference
        root_obj_cls_name = 'Reference'
        ref = Reference.objects.get(pk=obj.reference_id)
        title = ref.title
        comment = obj.description
        link = request and request.build_absolute_uri(
                   reverse('bibliography:reference_detail',
                           kwargs={'reference_pk': obj.reference_id,
                                   'uref_id': obj.id})) \
               or "https://" + settings.DOMAIN + obj.get_absolute_url()
    if cls_name in ('Document', 'File', 'Image', 'Link', 'Video'):
        comment = obj.description
        link = request and request.build_absolute_uri(
                   reverse('documents:document_detail',
                           kwargs={'doc_pk': obj.id})) \
               or "https://" + settings.DOMAIN + obj.get_absolute_url()
    if cls_name == 'ThreadedComment':
        if obj.is_editorial_note:
            return
        author = ''
        user_link = request and request.build_absolute_uri(
                    reverse('profile',
                           kwargs={'pk': user.id})) \
                    or "https://" + settings.DOMAIN + user.get_absolute_url()
        disc_root = obj.discussion_root
        root_obj = disc_root.content_object
        root_obj_cls_name = root_obj.__class__.__name__

        if root_obj_cls_name == 'Site':
            root_obj_cls_name = 'Discussion'
            title = disc_root.title
            author = User.objects.get(pk=disc_root.user_id)
        elif root_obj_cls_name == 'ThreadedComment':
            root_obj_cls_name = 'Comment'
            title = root_obj.title
            author = User.objects.get(pk=root_obj.user_id)
        elif root_obj_cls_name == 'UserReference':
            from rlp.bibliography.models import Reference
            ref = Reference.objects.get(pk=root_obj.reference_id)
            title = ref.title
            author = User.objects.get(pk=root_obj.user_id)
            root_obj_cls_name = 'Reference'
        elif root_obj_cls_name == 'CaseReport':
            title = root_obj.title
            author = root_obj.primary_author
        elif root_obj_cls_name in ('Document', 'File', 'Image', 'Link', 'Video'):
            title = root_obj.title
            author = User.objects.get(pk=root_obj.owner_id)
        author_link = request and request.build_absolute_uri(
                      reverse('profile',
                           kwargs={'pk': author.id})) \
                      or "https://" + settings.DOMAIN + \
                         author.get_absolute_url()
        dash_link = request and \
                    request.build_absolute_uri(reverse('dashboard')) \
                    or "https://" + settings.DOMAIN

        if root_obj_cls_name == 'Discussion' and obj.title:
            template = 'core/emails/newdiscussion_comment_activity_email'
        else:
            template = 'core/emails/comment_activity_email'

        context.update({
            "user_link": user_link,
            "root_obj": root_obj,
            "author_link": author_link,
            "author": author,
            "dash_link": dash_link,
        })
        link = "https://" + settings.DOMAIN + obj.get_absolute_url()
        comment = obj.comment

    context.update({
        "user": user,
        "type": root_obj_cls_name,
        "title": title,
        "comment": comment,
        "link": link,
        "site": settings.DOMAIN,
    })

    if root_obj_cls_name == 'Discussion' and obj.title:
        subject = "{} shared a {} with you at Sarcoma Central"
    elif root_obj_cls_name == 'Reference' or root_obj_cls_name == 'UserReference':
        if cls_name == 'ThreadedComment':
            subject = "{} has shared a comment with you"
        else:
            subject = "{} has shared a reference with you"
    else:
        subject = "{{}} has shared a {} with you".format(root_obj_cls_name.lower())

    subject = subject.format(user.get_full_name(), root_obj_cls_name)

    template_name = "{}.txt".format(template)
    message_body = render_to_string(template_name, context)
    for member in recipients:
        mail = EmailMessage(subject,
                            message_body,
                            settings.DEFAULT_FROM_EMAIL,
                            [member,])
        mail.content_subtype = "html"
        mail.send()
