from actstream import action
from actstream.models import Action
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.lookups import DateTransform
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase

from rlp.core.utils import CREATION_VERBS
from rlp.managedtags.models import TaggedByManagedTag


@models.DateTimeField.register_lookup
class WeekTransform(DateTransform):
    lookup_name = 'week'


@models.DateTimeField.register_lookup
class ISOYearTransform(DateTransform):
    lookup_name = 'isoyear'


class SEOMixin(models.Model):
    title = models.CharField(max_length=255)
    page_title = models.CharField(max_length=255, blank=True, help_text="Overwrite the title (html title tag)")
    menu_title = models.CharField(max_length=55, blank=True, help_text="Overwrite the title in the menu")
    meta_description = models.CharField(max_length=155, blank=True, help_text="The text displayed in search engines.")
    slug = models.SlugField(max_length=255, unique=True)
    date_created = models.DateTimeField(editable=False, auto_now_add=True)
    date_updated = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def get_menu_title(self):
        return self.menu_title or self.title

    def get_meta_title(self):
        return self.page_title or self.title


class EmailLog(models.Model):
    """Used to log all outgoing transactional emails. Can be used to troubleshoot."""
    subject = models.CharField(max_length=200)
    message_text = models.TextField()
    message_html = models.TextField()
    to_email = models.EmailField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'To: {} Subject: {}'.format(self.to_email, self.subject[:10])


class SharedContent(models.Model):
    '''Associates target content with multiple project/user viewers'''

    viewer_id = models.TextField('project/user ID')
    viewer_type = models.ForeignKey(
        ContentType,
        verbose_name='viewer content type',
        related_name='viewer_type_set_for_%(class)s',
        on_delete=models.CASCADE,
    )
    viewer = GenericForeignKey(
        ct_field='viewer_type',
        fk_field='viewer_id',
    )
    target_id = models.TextField('target ID')
    target_type = models.ForeignKey(
        ContentType,
        verbose_name='target content type',
        related_name='target_type_set_for_%(class)s',
        on_delete=models.CASCADE,
    )
    target = GenericForeignKey(
        ct_field='target_type',
        fk_field='target_id',
    )

    def __str__(self):
        return u'"%s" shared with "%s"' % (self.target, self.viewer)


class SharedObjectMixin(models.Model):
    """ Bookmarkable
    """
    class Meta:
        abstract = True

    _related = GenericRelation(
        SharedContent,
        content_type_field='target_type',
        object_id_field='target_id',
    )
    # shareable is set to False when content is created from closed group
    shareable = models.BooleanField(
        editable=False,
        blank=True,
        default=True
    )
    tags = TaggableManager(blank=True)
    mtags = TaggableManager(through=TaggedByManagedTag,
                            help_text="A Comma separated list of UNAPPROVED tags.",
                            blank=True)

    @property
    def is_bookmarkable(self):
        return True


    def get_viewers(self):
        my_type = ContentType.objects.get_for_model(self)
        shares = Action.objects.filter(
            action_object_object_id=self.id,
            action_object_content_type=my_type,
            verb__exact='shared',
        )
        return {s.target for s in shares if s.target}

    def get_viewers_as_users(self):
        '''resolve group viewers into lists of individuals'''
        users = set()
        for vwr in self.get_viewers():
            if hasattr(vwr, 'users'):
                # project/group
                users.update(vwr.users.all())
            else:
                # individual user
                users.add(vwr)
        return users

    def get_poster(self):
        my_type = ContentType.objects.get_for_model(self)
        creation_action = Action.objects.filter(
            action_object_object_id=self.id,
            action_object_content_type=my_type,
            verb__in=CREATION_VERBS,
        ).first()
        if not creation_action:
            return
        return creation_action.actor

    def is_shared_with_user(self, user):
        return user in self.get_viewers_as_users() or user.is_superuser

    def is_bookmarked_to(self, viewer):
        '''see if a user or group has this bookmarked'''
        target = self
        if (hasattr(self, 'polymorphic_model_marker')
           and len(self._meta.parents)):
            # for polymorphic types, the parent reference is bookmarked
            parent_type = list(self._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=self.id)
        viewer_type = ContentType.objects.get_for_model(viewer)
        target_type = ContentType.objects.get_for_model(target)
        return bool(SharedContent.objects.filter(
            target_id=target.id,
            viewer_id=viewer.id,
            target_type_id=target_type.id,
            viewer_type_id=viewer_type.id,
        ))

    def share_with(self, viewers, shared_by, comment=None):
        # add an entry to the target viewer's activity stream
        for viewer in viewers:
            # ghf - need to create Actions to go along with this.
            is_public = True
            if shared_by == viewer:
                is_public = False
            action.send(
                shared_by,
                verb='shared',
                description=comment,
                action_object=self,
                target=viewer,
                public=is_public,
            )

    def get_content_type(self, resolve_polymorphic=True):
        target = self
        if (resolve_polymorphic
           and hasattr(self, 'polymorphic_model_marker')
           and len(self._meta.parents)):
            # for polymorphic types, share the parent reference
            parent_type = list(self._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=self.id)
        content_type = ContentType.objects.get_for_model(target)
        return content_type.natural_key()

    def get_content_type_id(self, resolve_polymorphic=True):
        target = self
        if (resolve_polymorphic
           and hasattr(self, 'polymorphic_model_marker')
           and len(self._meta.parents)):
            # for polymorphic types, share the parent reference
            parent_type = list(self._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=self.id)
        content_type = ContentType.objects.get_for_model(target)
        return content_type.id


    def notify_viewers(self, subject, context, template='emails/notification'):
        from rlp.core.email import send_transactional_mail
        for viewer in self.get_viewers_as_users():
            send_transactional_mail(
                viewer.email,
                subject,
                template,
                context
            )
