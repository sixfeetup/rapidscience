from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify


def reject_to_requester(request, membership, group):
    data = {
        'group': group.title,
        'link': request.build_absolute_uri(reverse(
                    'projects:projects_list',
                ))
    }
    subject = "Your request to join {}".format(group.title)
    template = "projects/emails/reject_to_requester"
    body = render_to_string('{}.txt'.format(template), data)
    mail = EmailMessage(subject, body,
                        "Rapid Science <support@rapidscience.org>",
                        [membership.user.email, ])
    mail.content_subtype = "html"
    mail.send()


def approve_to_requester(request, membership, group):
    data = {
        'user': request.user.get_full_name(),
        'group': group.title,
        'link': request.build_absolute_uri(reverse(
                    'projects:projects_detail',
                    kwargs={
                        'pk': group.id,
                        'slug': slugify(group.title),
                    },
                ))
    }
    subject = "Approval to join {}".format(group.title)
    template = "projects/emails/approve_to_requester"
    body = render_to_string('{}.txt'.format(template), data)
    mail = EmailMessage(subject, body,
                        "Rapid Science <support@rapidscience.org>",
                        [membership.user.email, ])
    mail.content_subtype = "html"
    mail.send()
