import logging
import re
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from casereport.constants import WorkflowState
from rlp.core.mixins import SharesContentMixin

from actstream.models import Action

logger = logging.getLogger(__name__)

phone_digits_re = re.compile(r'^(?:1-?)?(\d{3})[-\.]?(\d{3})[-\.]?(\d{4}).*$')


class Institution(models.Model):
    name = models.CharField(max_length=255)
    banner_image = models.ImageField(upload_to='institutions', blank=True)
    thumbnail_image = models.ImageField(upload_to='institutions', blank=True)
    city = models.CharField(_('city'), max_length=255, blank=True)
    state = models.CharField(_('state'), max_length=255, blank=True)
    country = models.CharField(_('country'), max_length=255, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InstitutionDomain(models.Model):
    institution = models.ForeignKey(Institution)
    domain = models.CharField(max_length=200)

    class Meta:
        unique_together = ['institution', 'domain']

    def __str__(self):
        return self.domain


class UserManager(BaseUserManager):
    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name.lower(), domain_part.lower()])
        return email

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, SharesContentMixin):
    """
    Email and password are required. Other fields are optional.
    """
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    title = models.CharField(max_length=255, blank=True, verbose_name='Position')
    department = models.CharField(max_length=255, blank=True, verbose_name='Department')
    degrees = models.CharField(max_length=20, blank=True, help_text='MD, PhD, etc.')
    bio = models.TextField(blank=True, max_length=3000)
    research_interests = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True, help_text='Enter the full url e.g. https://twitter.com/username')
    photo = models.ImageField(upload_to="profile_photos", blank=True)
    banner = models.ImageField(upload_to="banner_photos", blank=True)
    institution = models.ForeignKey(Institution, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def display_type(self):
        return mark_safe( '<a href="{url}">{repr}</a>'.format(url=self.get_absolute_url(), repr=str(self)))

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('profile', args=[self.pk])

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    @property
    def can_access_all_projects(self):
        # If the user is an admin, they can access any project on the site
        return self.is_staff

    def can_access_project(self, project):
        # if the user belongs to the project, they have access
        return self.is_staff or self in project.active_members()

    def active_projects(self):
        return self.projects.exclude(projectmembership__state='pending')

    def _get_my_activity_query(self):
        my_ct = ContentType.objects.get_for_model(self)
        q = Q(
            actor_content_type=my_ct,
            actor_object_id=self.id
        )
        return q

    def _get_activity_involving_me_query(self):
        my_ct = ContentType.objects.get_for_model(self)
        q = Q(
            target_content_type=my_ct,
            target_object_id=self.id
        )
        return q

    def _get_activity_excluding_self_shares(self):
        my_ct = ContentType.objects.get_for_model(self)
        # exclude shares with self
        q = ~Q(
            actor_content_type=my_ct,
            actor_object_id=self.id,
            verb__exact='shared',
            target_content_type=my_ct,
            target_object_id=self.id,
        )
        return q

    def _get_activity_in_my_projects_query(self):
        from rlp.projects.models import Project  # here to avoid circular import
        active_projects = self.active_projects()
        project_ct = ContentType.objects.get_for_model(Project)
        q = Q(
            target_content_type=project_ct,
            target_object_id__in=list(
                active_projects.values_list('id', flat=True))
        )
        return q

    def get_activity_stream(self, type_class=None):
        from casereport.models import CaseReport
        activity_stream_queryset = Action.objects.filter(
            (
                self._get_my_activity_query()
                | self._get_activity_involving_me_query()
                | self._get_activity_in_my_projects_query()
            )
            & self._get_activity_excluding_self_shares()
        )

        # exclude shares to me of casereports that arent mine and live,
        if True: #not self.is_staff:
            casereport_ct = ContentType.objects.get_for_model(CaseReport)
            my_ct = ContentType.objects.get_for_model(self)
            # not loving this, but cant use expressions like
            # action_object__workflow_state = 'live'
            # because django orm has no dynamic reverse relation
            casereports_shared_with_me_ids = activity_stream_queryset.filter(
                action_object_content_type=casereport_ct,
                verb__exact='shared',
                # target_content_type_id=my_ct,
                # target_object_id=self.id,
            ).exclude(actor_content_type=my_ct,
                      actor_object_id=self.id,
                      ).values_list('action_object_object_id', flat=True)
            logger.debug("shared crs", list(casereports_shared_with_me_ids))
            non_live_ids = CaseReport.objects.filter(
                id__in=list(casereports_shared_with_me_ids)) \
                .exclude(workflow_state=WorkflowState.LIVE) \
                .values_list('id', flat=True)
            logger.debug("nonlive crs", list(non_live_ids))
            activity_stream_queryset = activity_stream_queryset.exclude(
                action_object_content_type=casereport_ct,
                action_object_object_id__in=list(
                    non_live_ids))  # would love to know why list was need here, but not in the query above.
        return activity_stream_queryset


class UserLogin(models.Model):
    user = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} logged in {}".format(self.user.get_full_name(), self.date_created.strftime("%Y-%m-%d %H:%M:%S %z"))
