from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import created
from .models import CaseReport
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=CaseReport)
def casereport_saved(sender, **kwargs):
    if not kwargs.get('created'):
        return
    report = kwargs.get('instance')
    created(report)


@receiver(post_save, sender=User)
def author_updated(sender, **kwargs):
    '''reindex an author's case reports when their profile is updated'''
    if kwargs.get('update_fields') == {'last_login'}:
        # ignore update during login
        return
    user = kwargs.get('instance')
    authored = Q(primary_author=user)
    co_authored = Q(co_author=user)
    user_reports = CaseReport.objects.filter(authored | co_authored)
    for cr in user_reports:
        post_save.send(sender=CaseReport, instance=cr)
