from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify

from rlp.accounts.models import User


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


def project_invite_member(request, invitees, project, message):
    # invitees should be a list of email addresses
    project_url = request.build_absolute_uri(
        reverse('projects:projects_detail',
                kwargs={'pk': project.pk, 'slug': project.slug}))
    projects_list = request.build_absolute_uri(
        reverse('projects:projects_list'))
    join_url = request.build_absolute_uri(
        reverse('projects:projects_join',
                kwargs={'pk': project.pk}))
    user_url = request.build_absolute_uri(
        reverse('profile',
                kwargs={'pk': request.user.pk}))
    mods = project.users.filter(projectmembership__state='moderator')
    if len(mods) == 1:
        pre_mod_text = "moderator is "
    else:
        pre_mod_text = "moderators are "
    mods = ' and '.join([x.get_full_name() for x in mods])
    data = {
        'user': request.user.get_full_name(),
        'user_link': user_url,
        'project_title': project.title,
        'project_join': join_url,
        'project_link': project_url,
        'projects_list': projects_list,
        'message': message,
        'mods': pre_mod_text + mods
    }
    subject = "{0} invites you to join {1}".format(
        request.user.get_full_name(),
        project.title)
    template = "projects/emails/member_group_invite"
    body = render_to_string('{}.txt'.format(template), data)
    mail = EmailMessage(subject, body,
                        "Rapid Science <support@rapidscience.org>",
                        [member for member in invitees])
    mail.content_subtype = "html"
    mail.send()


def project_invite_nonmember(request, invitees, project, message):
    # invitees is a list of email addresses.
    # Create an inactive account for each
    for ext in invitees:
        try:
            # check if member already exists, send the member email
            member = User.objects.get(email=ext)
            if member.is_active:
                project_invite_member(request, [member.email], project, message)
                return
            # else send the nonmember email
        except User.DoesNotExist:
            member = User(email=ext, is_active=False)
            member.save()

        project_url = request.build_absolute_uri(
            reverse('projects:projects_detail',
                    kwargs={'pk': project.pk, 'slug': project.slug}))
        join_url = request.build_absolute_uri(
            reverse('projects:projects_join',
                    kwargs={'pk': project.pk}))
        user_url = request.build_absolute_uri(
            reverse('profile', kwargs={'pk': request.user.pk}))
        register_url = request.build_absolute_uri(
            reverse('register_user', kwargs={'pk': member.pk}))
        data = {
            'user': request.user.get_full_name(),
            'user_link': user_url,
            'project_title': project.title,
            'join_link': join_url,
            'project_link': project_url,
            'reg_link': register_url,
            'message': message
        }
        subject = "Invitation to join {}".format(project.title)
        template = "projects/emails/nonmember_group_invite"
        body = render_to_string('{}.txt'.format(template), data)
        mail = EmailMessage(subject, body,
                            "Rapid Science <support@rapidscience.org>",
                            [member.email, ])
        mail.content_subtype = "html"
        mail.send()
