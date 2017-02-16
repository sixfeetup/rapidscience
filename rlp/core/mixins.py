from actstream.models import Action
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

    def get_activity_stream(self, type_class=None):
        shared = self.get_shared_content(type_class)
        obj_ids = [obj.id for obj in shared]
        obj_types = [ContentType.objects.get_for_model(obj) for obj in shared]
        return Action.objects.filter(
            action_object_object_id__in=obj_ids,
            action_object_content_type__in=obj_types,
        )
