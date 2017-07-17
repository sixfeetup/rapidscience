import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

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
    if target == user:
        return
    comment = ""
    link = ""
    recipients = target.active_members()
    recipients = [member.get_full_name() + " <" + member.email + ">"
                  for member in recipients if member != user]
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
        link = request.build_absolute_uri(
                   reverse('bibliography:reference_detail',
                           kwargs={'reference_pk': obj.reference_id,
                                   'uref_id': obj.id}))
    if type in ('Document', 'Image', 'Link', 'Video'):
        comment = obj.description
        link = request.build_absolute_uri(
                   reverse('documents:document_detail',
                           kwargs={'doc_pk': obj.id}))
    context = {
        "user": user,
        "type": type,
        "title": title,
        "comment": comment,
        "link": link
    }
    subject = "{} shared a {} with you at Sarcoma Central"
    subject = subject.format(user.get_full_name(), type)
    template = 'core/emails/activity_email'
    message_body = render_to_string('{}.txt'.format(template), context)
    for member in recipients:
        mail = EmailMessage(subject,
                            message_body,
                            "support@rapidscience.org",
                            [member,])
        mail.content_subtype = "html"
        mail.send()
