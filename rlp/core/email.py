import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from rlp.accounts.models import User
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
    context = {}
    comment = ""
    link = ""
    template = 'core/emails/activity_email'
    recipients = set()
    # is target a project
    if hasattr(target, 'users'):
        #list(map(recipients.add, target.active_members()))
        for m in target.active_members():
            recipients.add(m)
    else:
    # else it is a list of members/groups
        for item in target:
            if hasattr(item, 'users'):
                #list(map(recipients.add, item.active_members()))
                for m in item.active_members():
                    recipients.add(m)
            else:
                recipients.add(item)

    # exclude anyone who has opted out
    #recipients = {r for r in recipients if not r.opt_out_of_email}
    allowed_recipients = set()
    for r in recipients:
        if hasattr(r, 'opt_out_of_email') and r.opt_out_of_email:
            pass
        else:
            allowed_recipients.add(r)

    recipients = [member.get_full_name() + " <" + member.email + ">"
                  for member in allowed_recipients if member != user]
    type = obj.__class__.__name__
    try:
        title = obj.title
    except AttributeError:
        title = ''
    if type == 'UserReference':
        from rlp.bibliography.models import Reference
        type = 'Reference'
        ref = Reference.objects.get(pk=obj.reference_id)
        title = ref.title
        comment = obj.description
        link = request and request.build_absolute_uri(
                   reverse('bibliography:reference_detail',
                           kwargs={'reference_pk': obj.reference_id,
                                   'uref_id': obj.id})) \
               or "https://" + settings.DOMAIN + obj.get_absolute_url()
    if type in ('Document', 'File', 'Image', 'Link', 'Video'):
        comment = obj.description
        link = request and request.build_absolute_uri(
                   reverse('documents:document_detail',
                           kwargs={'doc_pk': obj.id})) \
               or "https://" + settings.DOMAIN + obj.get_absolute_url()
    if type == 'ThreadedComment':
        if obj.is_editorial_note:
            return
        author = ''
        user_link = request and request.build_absolute_uri(
                    reverse('profile',
                           kwargs={'pk': user.id})) \
                    or "https://" + settings.DOMAIN + user.get_absolute_url()
        disc_root = obj.discussion_root
        root_obj = disc_root.content_object
        type = root_obj.__class__.__name__
        if type == 'Site':
            type = 'Discussion'
            title = disc_root.title
            author = User.objects.get(pk=disc_root.user_id)
        elif type == 'ThreadedComment':
            type = 'Comment'
            title = root_obj.title
            author = User.objects.get(pk=root_obj.user_id)
        elif type == 'UserReference':
            from rlp.bibliography.models import Reference
            ref = Reference.objects.get(pk=root_obj.reference_id)
            title = ref.title
            author = User.objects.get(pk=root_obj.user_id)
        elif type == 'CaseReport':
            title = root_obj.title
            author = root_obj.primary_author
        elif type in ('Document', 'File', 'Image', 'Link', 'Video'):
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
        "type": type,
        "title": title,
        "comment": comment,
        "link": link,
        "site": settings.DOMAIN,
    })
    subject = "{} shared a {} with you at Sarcoma Central"
    subject = subject.format(user.get_full_name(), type)
    message_body = render_to_string('{}.txt'.format(template), context)
    for member in recipients:
        mail = EmailMessage(subject,
                            message_body,
                            settings.DEFAULT_FROM_EMAIL,
                            [member,])
        mail.content_subtype = "html"
        mail.send()
