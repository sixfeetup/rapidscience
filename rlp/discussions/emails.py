from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify


def author_note_to_admin(request, casereport):
    slug = slugify(casereport.title)
    email_context = {
        "casereport": casereport,
        "comment": request.POST['comment'],
        "link": request.build_absolute_uri(reverse(
            'casereport_detail',
            kwargs={
                'case_id': casereport.pk,
                'title_slug': slug
            }))
    }
    subject = "{} posted an Editorial Note".format(casereport.primary_author.get_full_name())
    template = 'discussions/emails/author_note_to_admin'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        ["Editorial team <edit@rapidscience.org>", ])
    mail.content_subtype = "html"
    mail.send()