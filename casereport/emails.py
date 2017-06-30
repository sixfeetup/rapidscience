from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def publish(casereport):
    email_context = {
        "casereport": casereport
    }
    subject = "Your case report is live!"
    template = 'casereport/emails/authors_casereport_published'
    message_body = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject, message_body,
                        "Cases Central <edit@rapidscience.org>",
                        [casereport.primary_author.get_full_name() + ", <" +
                         casereport.primary_author.email + ">", ])
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
