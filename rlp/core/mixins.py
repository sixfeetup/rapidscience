from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .models import SharedContent
from casereport.models import CaseReport
from rlp.discussions.models import ThreadedComment


class SharesContentMixin(models.Model):
    class Meta:
        abstract = True

    _shared = GenericRelation(
        SharedContent,
        content_type_field='viewer_type',
        object_id_field='viewer_id',
    )

    def get_discussions(self):
        discussion_type = ContentType.objects.get_for_model(ThreadedComment)
        disc_refs = self._shared.select_related('target_type').filter(
            target_type=discussion_type
        )
        return [dr.target for dr in disc_refs]

    def get_casereports(self):
        report_type = ContentType.objects.get_for_model(CaseReport)
        cr_refs = self._shared.select_related('target_type').filter(
            target_type=report_type
        )
        return [crr.target for crr in cr_refs]
