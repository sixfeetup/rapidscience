from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from rlp.accounts.models import User


class Folder(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    name = models.CharField(max_length=50, blank=True)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType,
                                     verbose_name='content type',
                                     related_name="content_type_set_for_%(class)s",
                                     on_delete=models.CASCADE)
    object_pk = models.TextField('object ID')
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        if self.name:
            return self.name
        if self.content_type.model == 'projectreference':
            name = str(self.content_object.reference)
        else:
            name = str(self.content_object)
        if len(name) > 50:
            return '{}...'.format(name[:45])
        return name

