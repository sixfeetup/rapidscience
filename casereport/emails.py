from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify

from rlp.core.utils import resolve_email_targets

def publish_to_author(casereport):
    targets = [casereport.primary_author.email, ]
    #resolve_email_targets(casereport.primary_author)
    if not targets:
        return
    email_context = {
        "casereport": casereport
    }
    subject = "Your case report is live!"
    template = 'casereport/emails/authors_casereport_published'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        targets)
    mail.content_subtype = "html"
    mail.send()


def publish_to_group(casereport, groups):
    recipients = resolve_email_targets(groups,
                                       exclude=casereport.primary_author)

    email_context = {
        "casereport": casereport,
        "casescentral": reverse('haystac'),
        "site": settings.DOMAIN,
        "reg_link": reverse('register')
    }
    name = casereport.primary_author.get_full_name()
    subject = "{} shared a case report with you".format(name)
    template = 'casereport/emails/group_casereport_published'
    message_body = render_to_string('{}.txt'.format(template),
                                    email_context)
    for member in recipients:
        mail = EmailMessage(subject,
                            message_body,
                            "Cases Central <edit@rapidscience.org>",
                            [member,])
        mail.content_subtype = "html"
        mail.send()


def submitted(casereport):
    email_context = {
        "casereport": casereport
    }
    author_email_addresses = [casereport.primary_author.email,]
    #resolve_email_targets(casereport.primary_author)
    if not author_email_addresses:
        return
    subject = "Your case report submission"
    template = 'casereport/emails/authors_casereport_submitted'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        author_email_addresses,
                        cc=('edit@rapidscience.org',), )
    mail.content_subtype = "html"
    mail.send()


def send_back(casereport):
    email_context = {
        "casereport": casereport,
        "site": settings.DOMAIN,
    }
    subject = "Your case report is ready for review"
    template = 'casereport/emails/send_back_to_author'
    message_body = render_to_string('{}.txt'.format(template), email_context)
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
        'link': casereport.get_absolute_url(),
        'site': settings.DOMAIN
    }
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipient = casereport.primary_author.email
    # never used?
    message = EmailMessage(subject,
                           message_body,
                           "Cases Central <edit@rapidscience.org>",
                           ["Editorial team <edit@rapidscience.org>",])
    message.content_subtype = 'html'
    message.send()


def invite_people(casereport, email_addr):
    slug = slugify(casereport.title)
    email_context = {
        'site': settings.DOMAIN,
        "casereport": casereport,
        "casescentral": reverse('haystac'),
        "case_url": reverse(
            'casereport_detail',
            kwargs={
                'case_id': casereport.pk,
                'title_slug': slug
            }),
        "reg_link": reverse('register'),
    }
    subject = "{0} shared a case report with you".format(casereport.primary_author.get_full_name())
    template = 'casereport/emails/invite_people'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [email_addr, ])
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
    recipients = resolve_email_targets(user, exclude=casereport.primary_author)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        recipients)
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
    recipients = resolve_email_targets(user, exclude=casereport.primary_author)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        recipients)
    mail.content_subtype = "html"
    mail.send()


def cr_published_notifications(casereport):
    """When a case report has been published, send out
       the emails to those it has been shared with
    """
    shared_with = casereport.get_viewers()
    for viewer in resolve_email_targets(shared_with,
                                        exclude=casereport.primary_author):
        invite_people(casereport,viewer)
