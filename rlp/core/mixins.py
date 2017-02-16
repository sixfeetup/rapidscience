from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .models import SharedContent


class SharesContentMixin(models.Model):
    class Meta:
        abstract = True

    _shared = GenericRelation(
        SharedContent,
        content_type_field='viewer_type',
        object_id_field='viewer_id',
    )

    def get_shared_content(self, type_class=None):
        if type_class is None:
            refs = self._shared.all()
        else:
            content_type = ContentType.objects.get_for_model(type_class)
            refs = self._shared.select_related('target_type').filter(
                target_type=content_type
            )
        return [r.target for r in refs]

