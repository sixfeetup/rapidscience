from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify

from actstream.models import Action
from rlp.core.utils import resolve_email_targets


def publish_to_author(casereport):
    targets = [casereport.primary_author.email, ]
    # resolve_email_targets(casereport.primary_author)
    if not targets:
        return
    email_context = {
        "site": settings.DOMAIN,
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


def published(casereport, recipients):
    """
    :param casereport:
    :param recipients:
    :return:

    uses user preferences
    """
    allowed_recipients = resolve_email_targets(recipients,
                                               exclude=casereport.primary_author, )

    if not allowed_recipients:
        return

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
    for member in allowed_recipients:
        mail = EmailMessage(subject,
                            message_body,
                            "Cases Central <edit@rapidscience.org>",
                            [member])
        mail.content_subtype = "html"
        mail.send()


def created(casereport):
    email_context = {
        'casereport': casereport,
        'link': 'https://{}{}'.format(
            settings.DOMAIN,
            casereport.get_absolute_url(),
        )
    }
    subject = 'A case report has been created'
    template = 'casereport/emails/casereport_created.txt'
    message_body = render_to_string(template, email_context)
    mail = EmailMessage(
        subject, message_body,
        'Cases Central <edit@rapidscience.org>',
        ['edit@rapidscience.org'],
    )
    mail.content_subtype = 'html'
    mail.send()


def submitted(casereport):
    email_context = {
        "casereport": casereport,
        'link': casereport.get_absolute_url(),
        'site': settings.DOMAIN,
    }
    author_email_addresses = [casereport.primary_author.email, ]
    # resolve_email_targets(casereport.primary_author)
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
        'site': settings.DOMAIN,
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


def revise(casereport, user):
    if user.is_superuser:
        template = 'casereport/emails/revise_to_author.txt'
        subject = 'Your case report is being edited'
        user = casereport.primary_author
        recipient = user.email
    else:
        template = 'casereport/emails/revise_to_admin.txt'
        subject = 'Case Report Has Been Retracted'
        recipient = 'Editorial team <edit@rapidscience.org>'
    email_context = {
        "casereport": casereport,
        'title': casereport.title,
        'link': casereport.get_absolute_url(),
        'site': settings.DOMAIN,
        'number': casereport.pk,
        'user': user,
    }
    message_body = render_to_string(template, email_context)
    message = EmailMessage(
        subject,
        message_body,
        'Cases Central <edit@rapidscience.org>',
        [recipient],
    )
    message.content_subtype = 'html'
    message.send()


def invite_people(casereport, email_addr, comment=''):
    slug = slugify(casereport.title)
    email_context = {
        'site': settings.DOMAIN,
        "casereport": casereport,
        "invite_msg": comment,
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
        "site": settings.DOMAIN,
        "casereport": casereport,
        "user": user
    }
    author = casereport.primary_author.get_full_name()
    subject = "{0} invites you to co-author a case report".format(author)
    template = 'casereport/emails/invite_coauthor'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    recipients = resolve_email_targets(user, force=True,
                                       exclude=casereport.primary_author)
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
    recipients = resolve_email_targets(user, force=True,
                                       exclude=casereport.primary_author)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        recipients)
    mail.content_subtype = "html"
    mail.send()


def get_invite_comment(cr, viewer):
    # find action for this share, so we can get the comment
    actions = Action.objects.filter(
        target_object_id=viewer.id,
        action_object_content_type=85,
        action_object_object_id=cr.id)
    # loop through actions if multiple, get the latest comment
    for action in actions.extra(order_by=['-timestamp']):
        if not action.description:
            continue
        return action.description
    return ''


def cr_published_notifications(casereport):
    """When a case report has been published, send out
       the emails to those it has been shared with.
       Uses user email preferences.
    """
    shared_with = casereport.get_viewers()
    for viewer in shared_with:
        sendto = resolve_email_targets(viewer,
                                       exclude=casereport.primary_author)
        comment = get_invite_comment(casereport, viewer)
        if sendto:
            invite_people(casereport, sendto, comment=comment)
    # specifically send to the non-members, who get an account
    # created with the email digest option, so they are not
    # returned in the resolve_email_targets()
    for viewer in shared_with:
        if hasattr(viewer, 'is_active') and not viewer.is_active:
            comment = get_invite_comment(casereport, viewer)
            invite_people(casereport, viewer.email, comment=comment)
