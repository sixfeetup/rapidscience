from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .models import SharedContent
from casereport.models import CaseReport
from rlp.discussions.models import ThreadedComment
from rlp.documents.models import Document


class SharesContentMixin(models.Model):
    class Meta:
        abstract = True

    _shared = GenericRelation(
        SharedContent,
        content_type_field='viewer_type',
        object_id_field='viewer_id',
    )

    def _get_shared_objects(self, type_class):
        content_type = ContentType.objects.get_for_model(type_class)
        refs = self._shared.select_related('target_type').filter(
            target_type=content_type
        )
        return [r.target for r in refs]

    def get_discussions(self):
        return self._get_shared_objects(ThreadedComment)

    def get_casereports(self):
        return self._get_shared_objects(CaseReport)

    def get_documents(self):
        return self._get_shared_objects(Document)
