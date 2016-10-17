import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import EmailLog


def send_transactional_mail(to_email, subject, template, context):
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
    mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], headers=headers)
    mail.attach_alternative(html_message, 'text/html')
    return mail.send()
