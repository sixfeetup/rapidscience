from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify


def publish_to_author(casereport):
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


def publish_to_group(casereport, groups):
    recipients = []
    if not groups:
        return
    for group in groups:
        recipients += group.active_members()
    recipients = set(recipients)
    recipients = [member.get_full_name() + " <" + member.email + ">"
                  for member in recipients]
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
    site = Site.objects.all()[0]
    email_context = {
        "casereport": casereport,
        "site": site
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
    site = Site.objects.all()[0]
    subject = "A case report has been updated and is ready for your review"
    template = 'casereport/emails/approved_to_admin'
    email_context = {
        'title': casereport.title,
        'link': casereport.get_absolute_url(),
        'site': site
    }
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipient = casereport.primary_author.email
    message = EmailMessage(subject,
                           message_body,
                           "Cases Central <edit@rapidscience.org>",
                           ["Editorial team <edit@rapidscience.org>",])
    message.content_subtype = 'html'
    message.send()


def invite_people(casereport, user):
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
        "reg_link": reverse(
            'register_user',
            kwargs={'pk': user.pk})
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


def cr_published_notifications(casereport):
    """When a case report has been published, send out
       the emails to those it has been shared with
    """
    shared_with = casereport.get_viewers()
    for viewer in shared_with:
        if hasattr(viewer, 'active_members'):
            publish_to_group(casereport, [viewer])
        else:
            invite_people(casereport, viewer)
