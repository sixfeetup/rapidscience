from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


def verify_email(request, user, key):
    subject = "Membership in Sarcoma Central"
    email_context = {
        'name': user.get_full_name(),
        'email': user.email,
        'link': request.build_absolute_uri(reverse(
            'registration_confirm',
            kwargs={
                'activation_key': key,
            },
        )),
    }
    template = 'registration/emails/verify_email'
    message = render_to_string('{}.txt'.format(template), email_context)
    mail = EmailMessage(subject,
                        message,
                        "Rapid Science <support@rapidscience.org>",
                        [user.email])
    mail.content_subtype = "html"
    mail.send()


def registration_to_admin(request, user, key):
    subject = "New registration pending approval"
    email_context = {
        'name': user.get_full_name(),
        'email': user.email,
        'link': request.build_absolute_uri(reverse(
                    'registration_activate',
                    kwargs={
                        'activation_key': key,
                    },
                )),
    }
    template = 'registration/emails/registration_to_admin'
    message = render_to_string('{}.txt'.format(template), email_context)
    to = ("Sarcoma Central admin <support@rapidscience.org>",)
    mail = EmailMessage(subject,
                        message,
                        "Rapid Science <support@rapidscience.org>",
                        to,
                        cc=('sg@rapidscience.org',))
    mail.content_subtype = "html"
    mail.send()


def acceptance_to_newuser(request, user):
    subject = "Membership in Sarcoma Central - welcome and a few tips"
    email_context = {
        'name': user.get_full_name(),
        'commons_link': request.build_absolute_uri(reverse(
                    'projects:projects_detail',
                    kwargs={
                        'pk': 1,
                        'slug': 'community-commons',
                    },
                )),
        'groups_link': request.build_absolute_uri(reverse(
                    'projects:projects_list',
                )),
    }
    template = 'registration/emails/acceptance_to_newuser'
    message = render_to_string('{}.txt'.format(template), email_context)
    to = (user.get_full_name() + "<" + user.email + ">",)
    mail = EmailMessage(subject,
                        message,
                        "Rapid Science <support@rapidscience.org>",
                        to,)
    mail.content_subtype = "html"
    mail.send()
