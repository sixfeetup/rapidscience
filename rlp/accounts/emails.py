from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings


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
                        settings.DEFAULT_FROM_EMAIL,
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
    to = (settings.DEFAULT_FROM_EMAIL,)
    mail = EmailMessage(subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        to,
                        cc=settings.BCC_LIST)
    mail.content_subtype = "html"
    mail.send()


def acceptance_to_newuser(request, user):
    subject = "Membership in Sarcoma Central - joining groups and other tips"
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
        'login_url': request.build_absolute_uri(reverse('login')),
        'site': settings.DOMAIN,
    }
    template = 'registration/emails/acceptance_to_newuser'
    message = render_to_string('{}.txt'.format(template), email_context)
    to = (user.get_full_name() + "<" + user.email + ">",)
    mail = EmailMessage(subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        to,)
    mail.content_subtype = "html"
    mail.send()


def send_welcome(request, user):
    # for new users that did not need verification
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
        'login_url': request.build_absolute_uri(reverse('login')),
        'site': settings.DOMAIN,
    }
    template = 'registration/emails/registration_welcome'
    message = render_to_string('{}.txt'.format(template), email_context)
    to = (user.get_full_name() + "<" + user.email + ">",)
    mail = EmailMessage(subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        to,)
    mail.content_subtype = "html"
    mail.send()


def accepted_members_notification_to_admin(request, user, key):
    subject = "New registration from automatically accepted user"
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
    template = 'registration/emails/accepted_members_notification_to_admin'
    message = render_to_string('{}.txt'.format(template), email_context)
    to = (settings.DEFAULT_FROM_EMAIL,)
    mail = EmailMessage(subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL_RAPID_SCIENCE,
                        to,
                        cc=settings.BCC_LIST)
    mail.content_subtype = "html"
    mail.send()
