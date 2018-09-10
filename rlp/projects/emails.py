from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.conf import settings

from rlp.accounts.models import User
from rlp.projects.models import ProjectMembership


def reject_to_requester(request, membership, group):
    if not membership.user.notify_immediately:
        return
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
                        settings.DEFAULT_FROM_EMAIL,
                        [membership.user.email, ])
    mail.content_subtype = "html"
    mail.send()


def approve_to_requester(request, membership, group):
    if not membership.user.notify_immediately:
        return
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
                        settings.DEFAULT_FROM_EMAIL,
                        [membership.user.email, ])
    mail.content_subtype = "html"
    mail.send()


# TODO: now that these next two are so similar, combine them.
def invite_existing_member_to_group(request, invitees, project, message):
    # invitees should be a list of email addresses
    # project_url = request.build_absolute_uri(
    #     reverse('projects:projects_detail',
    #             kwargs={'pk': project.pk, 'slug': project.slug}))
    projects_list = request.build_absolute_uri(
        reverse('projects:projects_list'))
    join_url = request.build_absolute_uri(
        reverse('projects:projects_join',
                kwargs={'pk': project.pk}))
    # user_url = request.build_absolute_uri(
    #     reverse('profile',
    #             kwargs={'pk': request.user.pk}))
    # mods = project.users.filter(projectmembership__state='moderator')
    # if len(mods) == 1:
    #     pre_mod_text = "moderator is "
    # else:
    #     pre_mod_text = "moderators are "
    # mods = ' and '.join([x.get_full_name() for x in mods])
    data = {
        'user': request.user.get_full_name(),
        'project_title': project.title,
        'project_join': join_url,
        'projects_list': projects_list,
        'message': message,
    }
    subject = "{0} invites you to join {1}".format(
        request.user.get_full_name(),
        project.title)
    template = "projects/emails/invite_existing_member_to_group"
    body = render_to_string('{}.txt'.format(template), data)

    for member in invitees:
        mail = EmailMessage(subject=subject,
                            body=body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            bcc=[member]
                            )
        mail.content_subtype = "html"
        mail.send()


def invite_nonmember_to_group(request, invitees, project, message):
    # invitees is a list of email addresses.
    # Create an inactive account for each
    for ext in invitees:
        try:
            # check if member already exists, send the member email
            member = User.objects.get(email=ext)
            if member.is_active:
                invite_existing_member_to_group(request, [member.email], project, message)
                return
            # else send the nonmember email
        except User.DoesNotExist:
            member = User(email=ext, is_active=False)
            member.save()

        # project_url = request.build_absolute_uri(
        #     reverse('projects:projects_detail',
        #             kwargs={'pk': project.pk, 'slug': project.slug}))
        join_url = request.build_absolute_uri(
            reverse('projects:projects_join',
                    kwargs={'pk': project.pk}))
        projects_list = request.build_absolute_uri(
            reverse('projects:projects_list'))
        # user_url = request.build_absolute_uri(
        #     reverse('profile', kwargs={'pk': request.user.pk}))
        register_url = request.build_absolute_uri(
            reverse('register_user', kwargs={'pk': member.pk}))
        data = {
            'user': request.user.get_full_name(),
            'project_title': project.title,
            'project_join': join_url,
            'projects_list': projects_list,
            'message': message,
            'reg_link': register_url,
        }
        subject = "Invitation to join {}".format(project.title)
        template = "projects/emails/invite_non_member_to_group"
        body = render_to_string('{}.txt'.format(template), data)
        mail = EmailMessage(subject, body,
                            settings.DEFAULT_FROM_EMAIL,
                            [member.email, ])
        mail.content_subtype = "html"
        mail.send()


def join_request_to_mods(request, project):
    subject = "Request to join your closed group"
    mods = [mod.get_full_name() + " <" + mod.email + ">" for mod
            in project.users.filter(projectmembership__state='moderator')]
    cc = [settings.DEFAULT_FROM_EMAIL,]
    membership = ProjectMembership.objects.get(project_id=project.id,
                                                  user_id=request.user.id)
    link = request.build_absolute_uri(
            reverse('projects:accept_membership_request',
                    kwargs={'membership_id': membership.id}))
    data = {
        'user': request.user,
        'project': project,
        'link': link
    }
    template = "projects/emails/join_request_to_mods"
    body = render_to_string('{}.txt'.format(template), data)
    mail = EmailMessage(subject, body,
                        settings.DEFAULT_FROM_EMAIL,
                        mods, cc=cc)
    mail.content_subtype = "html"
    mail.send()
