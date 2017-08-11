from datetime import timedelta
import sys

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from django.utils import timezone

from actstream.models import Action

from rlp.accounts.models import User
from rlp.core.email import send_transactional_mail
from rlp.projects.models import Project


class Command(BaseCommand):
    """Sends a weekly summary of site activity. Should only be run once per week."""
    def handle(self, *args, **options):
        try:
            self.process()
        except Exception as err:
            subject = "{}".format(sys.argv[1])
            message = "{}".format(err)
            mail_admins(subject, message)
            raise

    def process(self):
        site = Site.objects.get_current()
        some_day_last_week = timezone.now().date() - timedelta(days=7)
        year, week, day = some_day_last_week.isocalendar()
        # Exclude shared references since this doesn't make sense to show to the full audience
        shared_ref_ct = ContentType.objects.get(app_label='bibliography', model='referenceshare')
        activity_stream = Action.objects.filter(
            timestamp__isoyear=year,
            timestamp__week=week
        ).exclude(action_object_content_type=shared_ref_ct)
        # Bail early if there wasn't any activity last week
        if not activity_stream.count():
            return
        activity_stream_for_open_projects = activity_stream.filter(
            target_content_type=ContentType.objects.get_for_model(Project),
            target_object_id__in=list(Project.objects.filter(approval_required=False).values_list('id', flat=True))
        )
        comment_ct = ContentType.objects.get(app_label='discussions', model='threadedcomment')
        biblio_ct = ContentType.objects.get(app_label='bibliography', model='reference')
        docs_cts = ContentType.objects.filter(app_label='documents')
        subject = "What's new in the {} Network".format(site.name)
        context_for_all_projects = {
            'comments': activity_stream.filter(action_object_content_type=comment_ct),
            'references': activity_stream.filter(action_object_content_type=biblio_ct),
            'docs': activity_stream.filter(action_object_content_type__in=docs_cts),
        }
        context_for_open_projects = {
            'comments': activity_stream_for_open_projects.filter(action_object_content_type=comment_ct),
            'references': activity_stream_for_open_projects.filter(action_object_content_type=biblio_ct),
            'docs': activity_stream_for_open_projects.filter(action_object_content_type__in=docs_cts),
        }
        for user in User.objects.filter(is_active=True):
            context = {
                'user': user
            }
            if user.can_access_all_projects:
                context.update(context_for_all_projects)
            else:
                # Skip if no activity for last week
                if not activity_stream_for_open_projects.count():
                    continue
                context.update(context_for_open_projects)
            send_transactional_mail(
                user.email,
                subject,
                'emails/weekly_summary',
                context
            )
