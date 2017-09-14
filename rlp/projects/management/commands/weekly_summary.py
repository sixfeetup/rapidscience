from datetime import timedelta
import sys

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
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
        some_day_last_week = timezone.now() - timedelta(days=7)
        year, week, day = some_day_last_week.isocalendar()
        # Exclude shared references since this doesn't make sense to show to the full audience
        shared_ref_ct = ContentType.objects.get(app_label='bibliography',
                                                model='referenceshare')
        activity_stream = Action.objects.filter(
            timestamp__gte=some_day_last_week,
            timestamp__lte=timezone.now()).exclude(
            action_object_content_type=shared_ref_ct)
        # Bail early if there wasn't any activity last week
        if not activity_stream.count():
            return
        # define the content types
        casereport_ct = ContentType.objects.get(app_label='casereport',
                                                model='casereport')
        comment_ct = ContentType.objects.get(app_label='discussions',
                                             model='threadedcomment')
        biblio_ct = ContentType.objects.get(app_label='bibliography',
                                            model='userreference')
        docs_cts = ContentType.objects.filter(app_label='documents')
        subject = "Weekly summary of new activity"

        # loop through users
        for user in User.objects.filter(is_active=True):
            if user.email_prefs != 'digest':
                print("skipping ", user, ": email setting is {0}".format(user.email_prefs))
                continue
            projects = user.active_projects()
            stream_for_user_projects = activity_stream.filter(
                target_content_type=ContentType.objects.get_for_model(Project),
                target_object_id__in=list(projects.values_list('id', flat=True))
            )
            email_context = {
                'user': user,
                'site': site
            }

            results = 0
            # loop through all content returned to strip out duplicates
            # (for when multiple actions happen on one pice of content)
            for ctype in [comment_ct, casereport_ct, docs_cts, biblio_ct]:
                display_items = []  # items to display in the email
                # docs_cts has multiple types we group together
                if ctype == docs_cts:
                    cxt_label = 'document'
                    for doctype in docs_cts:
                        content_id_set = []
                        all_content = stream_for_user_projects.filter(
                            action_object_content_type=doctype)
                        for item in all_content:
                            if item.action_object_object_id in content_id_set:
                                continue
                            content_id_set.append(item.action_object_object_id)
                            display_items.append(item)
                else:
                    content_id_set = []
                    cxt_label = ctype.model
                    all_content = stream_for_user_projects.filter(
                        action_object_content_type=ctype)
                    for item in all_content:
                        if item.action_object_object_id in content_id_set:
                            continue
                        content_id_set.append(item.action_object_object_id)
                        if ctype.model == 'threadedcomment' and not item.action_object.title:
                            continue
                        display_items.append(item)
                results += len(display_items)
                email_context.update({cxt_label: display_items})

            if not results:
                continue
            template = 'emails/weekly_summary'
            message_body = render_to_string('{}.txt'.format(template), email_context)
            mail = EmailMessage(subject, message_body,
                                "Sarcoma Central <support@rapidscience.org>",
                                [user.email])
            mail.content_subtype = "html"
            mail.send()
