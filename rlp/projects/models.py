from collections import defaultdict

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mass_mail
from django.db import models
from django_fsm import FSMField
from django_fsm import transition
from menus.menu_pool import menu_pool

from rlp.accounts.models import Institution
from rlp.core.email import send_transactional_mail
from rlp.core.mixins import SharesContentMixin
from rlp.core.models import SEOMixin

MEMBER_STATES = (
    ('moderator', 'Moderator'),
    ('member', 'Member'),
    ('pending', 'Applicant'),
)


class Topic(SEOMixin):
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']


class Project(SEOMixin, SharesContentMixin):
    cover_photo = models.ImageField(null=True, blank=True)
    institution = models.ForeignKey(Institution, blank=True, null=True)
    topic = models.ForeignKey(Topic, blank=True, null=True)
    approval_required = models.BooleanField(default=True,
                                            help_text='If checked, registrants must be approved before joining.')
    auto_opt_in = models.BooleanField('Automatically opt-in members', default=False,
                                      help_text='If checked, all members will be automatically added to this project.')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="ProjectMembership", related_name='projects')
    goal = models.CharField(max_length=450, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('projects:projects_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_documents_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'projects:projects_tab',
            kwargs={'pk': self.pk, 'slug': self.slug, 'tab': 'documents'},
        )

    def get_discussions_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'projects:projects_tab',
            kwargs={'pk': self.pk, 'slug': self.slug, 'tab': 'discussions'},
        )

    def get_bibliography_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'projects:projects_tab',
            kwargs={'pk': self.pk, 'slug': self.slug, 'tab': 'bibliography'},
        )

    def get_contact_email_addresses(self):
        emails = [
            pm.user.email for pm in
            ProjectMembership.objects.filter(state='moderator', project=self)
            ]
        emails += settings.REGISTRATION_REVIEWERS
        # One-off customization so that a single person could additionally be notified of 'approval required'
        # registrations, but only for projects that specifically require approval. We do NOT send to these recipients
        # if approval is required only because the user's email address didn't match their institution's domain.
        if self.approval_required:
            emails.extend(settings.REGISTRATION_REVIEWERS_FOR_APPROVAL_REQUIRED_PROJECTS)
        return emails

    def notify_members(self, subject, context, template='emails/notification'):
        for membership in self.projectmembership_set.filter(user__is_active=True):
            send_transactional_mail(
                membership.user.email,
                subject,
                template,
                context
            )

    def invite_registered_users(self, users, subject=None, message=None, inviter=None, extra_template_vars=None):
        emails = [u.email for u in users if u.email]
        return self.invite_external_emails(emails, subject, message, inviter, extra_template_vars)

    def invite_external_emails(self, emails, subject=None, message=None, inviter=None, extra_template_vars=None):
        """Send an invitation by email to each of the emails given."""
        subject = subject or 'Invitation to join {}'.format(self.title)
        message = message or settings.GROUP_INVITATION_TEMPLATE
        inviter = inviter or self.moderators().first()

        # format the message
        site = Site.objects.get_current()
        project_url = 'https://' + site.domain + self.get_absolute_url()
        context = defaultdict(
            str,
            user=inviter.email,
            group=self.title,
            link=project_url,
        )
        if extra_template_vars:
            context.update(extra_template_vars)
        message = message.format(**context)

        message_data = (
            (
                subject,
                message,
                inviter.get_full_name() + " <info@rapidscience.org>",
                [rcp],
            )
            for rcp in emails
        )
        print("sending", message_data)
        send_mass_mail(message_data)

    def save(self, *args, **kwargs):
        # Groups are in the top level navigation and need to clear the cache
        # on save.
        menu_pool.clear()
        super().save(*args, **kwargs)

    def active_members(self):
        return self.users.exclude(projectmembership__state='pending')

    def pending_members(self):
        return self.users.filter(projectmembership__state='pending')

    def moderators(self):
        return self.users.filter(projectmembership__state='moderator')

    def project_mods(self):
        mods = self.users.filter(projectmembership__state='moderator')
        return ' | '.join([x.get_full_name() for x in mods])

    def add_member(self, user):
        ''' add user to the project(group)
            if the user was already a member, no action is taken
            if the project requires membership approval, the user will be pending.
            otherwise a normal membership is made.

            Returns the ProjectMemebership  ( pending, member, moderator )
        '''

        initial_state = 'member'
        if self.approval_required:
            initial_state = 'pending'

        membership, is_new = ProjectMembership.objects.get_or_create(
            project=self,
            user=user,
            defaults={'state': initial_state},
        )

        return membership

    def remove_member(self, user):
        ''' remove user from the project.
        '''
        membership = self.projectmembership_set.get_or_create(user=user)
        membership.delete()


class ProjectMembership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    state = FSMField(choices=MEMBER_STATES, default='member')

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['project']

    def __str__(self):
        return "{user} is {state} of {project}".format(user=self.user.email, state=self.state,
                                                       project=self.project.title)

    @transition(field=state, source='*', target='moderator')
    def promote(self):
        pass

    @transition(field=state, source='moderator', target='member')
    def demote(self):
        pass

    @transition(field=state, source='pending', target='member')
    def approve(self):
        pass
