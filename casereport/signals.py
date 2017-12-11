from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import created
from .models import CaseReport


@receiver(post_save, sender=CaseReport)
def casereport_saved(sender, **kwargs):
    if not kwargs.get('created'):
        return
    report = kwargs.get('instance')
    created(report)
