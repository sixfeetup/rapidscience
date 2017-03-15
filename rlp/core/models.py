from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.lookups import DateTransform


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


class SharedObjectMixin(models.Model):
    class Meta:
        abstract = True

    _related = GenericRelation(
        SharedContent,
        content_type_field='target_type',
        object_id_field='target_id',
    )

    def get_viewers(self):
        refs = self._related.select_related('viewer_type').all()
        return [r.viewer for r in refs]

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

    def is_shared_with_user(self, user):
        return user in self.get_viewers_as_users()

    def share_with(self, viewers):
        target = self
        if (hasattr(self, 'polymorphic_model_marker')
           and len(self._meta.parents)):
            # for polymorphic types, share the parent reference
            parent_type = list(self._meta.parents)[-1]
            target = parent_type.objects.non_polymorphic().get(id=self.id)
        for viewer in viewers:
            SharedContent.objects.create(viewer=viewer, target=target)

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

    def notify_viewers(self, subject, context, template='emails/notification'):
        from rlp.core.email import send_transactional_mail
        for viewer in self.get_viewers_as_users():
            send_transactional_mail(
                viewer.email,
                subject,
                template,
                context
            )
