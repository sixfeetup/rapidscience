from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


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
