from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify


def publish(casereport):
    email_context = {
        "casereport": casereport
    }
    subject = "Your case report is live!"
    template = 'casereport/emails/authors_casereport_published'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [casereport.primary_author.get_full_name() + " <" +
                         casereport.primary_author.email + ">", ])
    mail.content_subtype = "html"
    mail.send()


def submitted(casereport):
    email_context = {
        "casereport": casereport
    }
    subject = "Your case report submission"
    template = 'casereport/emails/authors_casereport_submitted'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [casereport.primary_author.get_full_name() + " <" +
                         casereport.primary_author.email + ">", ],
                        cc=('edit@rapidscience.org',), )
    mail.content_subtype = "html"
    mail.send()


def send_back(casereport):
    subject = "Author Notification"
    message_body = "CaseReport {id} {url} has moved to {state}.".format(
        id=casereport.id, url=casereport.get_absolute_url(),
        state=casereport.get_workflow_state_display())

    recipient = casereport.primary_author.email
    message = EmailMessage(subject,
                           message_body,
                           "Cases Central <edit@rapidscience.org>",
                           [recipient])
    message.content_subtype = 'html'
    message.send()


def approved(casereport):
    subject = "A case report has been updated and is ready for your review"
    template = 'casereport/emails/approved_to_admin'
    email_context = {
        'title': casereport.title,
        'link': casereport.get_absolute_url()
    }
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipient = casereport.primary_author.email
    message = EmailMessage(subject,
                           message_body,
                           "Cases Central <edit@rapidscience.org>",
                           [settings.RSADMIN_EMAIL,])
    message.content_subtype = 'html'
    message.send()


def invite_people(request, casereport, user):
    slug = slugify(casereport.title)
    email_context = {
        "casereport": casereport,
        "casescentral": request.build_absolute_uri(reverse('haystac')),
        "case_url": request.build_absolute_uri(reverse(
            'casereport_detail',
            kwargs={
                'case_id': casereport.pk,
                'title_slug': slug
            })),
        "reg_link": request.build_absolute_uri(reverse(
            'register_user',
            kwargs={'pk': user.pk}))
    }
    subject = "{0} shared a case report with you".format(casereport.primary_author.get_full_name())
    template = 'casereport/emails/invite_people'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [user.email, ])
    mail.content_subtype = "html"
    mail.send()


def invite_coauthor(casereport, user):
    """Invite a co-author that is not currently a site member
    """
    email_context = {
        "casereport": casereport,
        "user": user
    }
    author = casereport.primary_author.get_full_name()
    subject = "{0} invites you to co-author a case report".format(author)
    template = 'casereport/emails/invite_coauthor'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipient = user.email
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [recipient])
    mail.content_subtype = "html"
    mail.send()


def notify_coauthor(casereport, user):
    """Notify a co-author that is a site member
    """
    email_context = {
        "casereport": casereport,
        "user": user
    }
    author = casereport.primary_author.get_full_name()
    subject = "{0} invites you to co-author a case report".format(author)
    template = 'casereport/emails/notify_coauthor'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipient = user.email
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [recipient])
    mail.content_subtype = "html"
    mail.send()