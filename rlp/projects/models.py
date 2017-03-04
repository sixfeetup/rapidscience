from django.conf import settings
from django.db import models
from django_fsm import FSMField
from django_fsm import transition

from filer.fields.image import FilerImageField
from menus.menu_pool import menu_pool

from rlp.accounts.models import Institution
from rlp.core.email import send_transactional_mail
from rlp.core.models import SEOMixin
from rlp.core.mixins import SharesContentMixin


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

    def save(self, *args, **kwargs):
        # Groups are in the top level navigation and need to clear the cache
        # on save.
        menu_pool.clear()
        super().save(*args, **kwargs)

    def active_members(self):
        return self.users.exclude(projectmembership__state='pending')

    def pending_members(self):
        return self.users.filter(projectmembership__state='pending')

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
            defaults={'state':initial_state},
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
        return "{user} is {state} of {project}".format(user=self.user.email, state=self.state, project=self.project.title)

    @transition(field=state, source='*', target='moderator')
    def promote(self):
        pass

    @transition(field=state, source='moderator', target='member')
    def demote(self):
        pass

    @transition(field=state, source='pending', target='member')
    def approve(self):
        pass
