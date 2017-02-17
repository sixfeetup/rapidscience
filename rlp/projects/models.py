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


class Topic(SEOMixin):
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']


class Role(models.Model):
    title = models.CharField(max_length=100)
    contact = models.BooleanField(default=False,
                                  help_text="If selected, users assigned this role may be treated as the point of "
                                            "contact for their project.")
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


PROJECT_STATES = (
    ('open', 'Open'),
    ('closed', 'Closed'),
)


class Project(SEOMixin, SharesContentMixin):
    cover_photo = FilerImageField(null=True, blank=True, related_name="project_photo")
    institution = models.ForeignKey(Institution, blank=True, null=True)
    topic = models.ForeignKey(Topic, blank=True, null=True)
    state = FSMField(choices=PROJECT_STATES, default='open')
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
        return reverse('projects:projects_documents', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_discussions_url(self):
        from django.core.urlresolvers import reverse
        return reverse('projects:projects_discussions', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_bibliography_url(self):
        from django.core.urlresolvers import reverse
        return reverse('projects:projects_bibliography', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_contact_email_addresses(self):
        emails = [pm.user.email for pm in ProjectMembership.objects.filter(role__contact=True, project=self)]
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

    @transition(field=state, source='closed', target='open')
    def open_group(self):
        pass

    @transition(field=state, source='open', target='closed')
    def close_group(self):
        # TODO should all shared content be taken from other groups/users?
        pass



class ProjectMembership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.ForeignKey(Role, blank=True, null=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['project']

    def __str__(self):
        return "Project membership for {}".format(self.user.email)
