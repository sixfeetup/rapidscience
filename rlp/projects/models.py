from collections import defaultdict

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_fsm import FSMField
from django_fsm import transition
from menus.menu_pool import menu_pool

from casereport.middleware import CurrentUserMiddleware
from rlp.accounts.models import Institution, User
from rlp.core.email import send_transactional_mail
from rlp.core.mixins import SharesContentMixin
from rlp.core.models import SEOMixin

from actstream.models import Action

from logging import getLogger
logger = getLogger('django')

MEMBER_STATES = (
    ('moderator', 'Moderator'),
    ('member', 'Member'),
    ('pending', 'Applicant'),
    ('ignored', 'Ignored Applicant')
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

    @property
    def display_type(self):
        return mark_safe('<a href="{url}">{repr}</a>'.format(url=self.get_absolute_url(), repr=self.title))

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('projects:projects_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_activity_stream(self, user=None, type_class=None):
        my_ct = ContentType.objects.get_for_model(self)
        activity_stream_queryset = Action.objects.filter(target_content_type=my_ct,
                                                 target_object_id=self.id)

        # TODO: consolidate this
        if user and not user.is_staff:
            from casereport.models import CaseReport
            casereport_ct = ContentType.objects.get_for_model(CaseReport)
            my_ct = ContentType.objects.get_for_model(self)
            # not loving this, but cant use expressions like
            # action_object__workflow_state = 'live'
            # because django orm has no dynamic reverse relation
            casereport_ids = activity_stream_queryset.filter(
                action_object_content_type=casereport_ct,
                verb__exact = 'shared',
                target_content_type_id=my_ct,
                target_object_id=self.id).values_list('action_object_object_id', flat=True)
            logger.debug( "shared crs %s", list(casereport_ids))
            non_live_ids = CaseReport.objects.filter(
                id__in=list(casereport_ids)).exclude(
                workflow_state='live').values_list('id', flat=True)
            logger.debug( "non live crs %s", list(non_live_ids))
            activity_stream_queryset = activity_stream_queryset.exclude(
                action_object_content_type=casereport_ct,
                action_object_object_id__in=list(
                    non_live_ids))  # would love to know why list was need here, but not in the query above.
        return activity_stream_queryset

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
        return self.users.exclude(projectmembership__state__in=('pending',
                                                                'ignored',))

    def pending_members(self):
        return self.users.filter(projectmembership__state='pending')

    def moderators(self):
        return self.users.filter(projectmembership__state='moderator')

    def project_mods(self):
        mods = self.users.filter(projectmembership__state='moderator')
        return ' | '.join([x.get_full_name() for x in mods])

    def add_member(self, user):
        """ add user to the project(group)
            if the user was already a member, no action is taken
            if the project requires membership approval, the user will be pending.
            otherwise a normal membership is made.

            Returns the ProjectMemebership  ( pending, member, moderator )
        """

        membership, is_new = ProjectMembership.objects.get_or_create(
            project=self,
            user=user,
        )

        # if moderator approval isn't needed, approve the member now
        if not self.approval_required:
            membership.state = 'member'
            membership.save()

        return membership

    def remove_member(self, user):
        """ remove user from the project.
        """
        membership = self.projectmembership_set.get_or_create(user=user)
        membership.delete()


class ProjectMembership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    state = FSMField(choices=MEMBER_STATES, default='pending')

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['project']

    def __str__(self):
        return "{user} is {state} of {project}".format(user=self.user.email, state=self.state,
                                                       project=self.project.title)

    @property
    def display_type(self):
        return "{user}'s request to join {group}".format(user=self.user, group=self.project)

    @transition(field=state, source='*', target='moderator')
    def promote(self):
        pass

    @transition(field=state, source='moderator', target='member')
    def demote(self):
        pass

    @transition(field=state, source='pending', target='member')
    def approve(self):
        # TODO: alert the user
        # activity stream entries for the user, the group and moderator
        # only log the approval if it wasn't automatic because the group was
        # open
        approver = CurrentUserMiddleware.get_user()
        if approver != self.user:
            approval_action = Action(actor=approver,
                                     verb='approved',
                                     action_object=self,
                                     target=self,)
            approval_action.save()

        # # this should show in the user's and project's activity feeds
        # user_action = Action(actor=self.user,
        #                      verb='joined',
        #                      action_object=self,
        #                      target=self.project,
        #                      public=False)
        # user_action.save()


    @transition(field=state, source='pending', target='ignored')
    def ignore(self):
        approver = CurrentUserMiddleware.get_user()
        # activity stream entries for the moderator
        denial = Action(actor=approver,
                        verb='denied',
                        action_object=self)
        denial.save()

        # this is to inform the user
        request_declined = Action(actor=approver,
                                  verb='declined',
                                  action_object=self,
                                  target=self.user)
        request_declined.save()
