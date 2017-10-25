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

from django.conf import settings

from rlp.accounts.models import User
from rlp.core.email import send_transactional_mail
from rlp.discussions.models import ThreadedComment
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
        # define the content types
        casereport_ct = ContentType.objects.get(app_label='casereport',
                                                model='casereport')
        comment_ct = ContentType.objects.get(app_label='discussions',
                                             model='threadedcomment')
        biblio_ct = ContentType.objects.get(app_label='bibliography',
                                            model='userreference')
        docs_cts = ContentType.objects.filter(app_label='documents')
        member_ct = ContentType.objects.get(model='user')
        subject = "Weekly summary of new activity"

        # loop through users
        for user in User.objects.filter(is_active=True):
            if user.email_prefs != 'digest':
                print("skipping ", user, ": email setting is {0}".format(user.email_prefs))
                continue
            projects = user.active_projects()
            email_context = {
                'user': user,
                'site': site,
                'user_groups': projects
            }

            results = 0
            comments = []
            # loop through all content returned to strip out duplicates
            # (for when multiple actions happen on one pice of content)
            for ctype in [comment_ct, casereport_ct, docs_cts, biblio_ct, member_ct]:
                display_items = []  # items to display in the email
                # docs_cts has multiple types we group together
                if ctype == docs_cts:
                    cxt_label = 'document'
                    for doctype in docs_cts:
                        content_id_set = []
                        all_content = user.get_activity_stream().filter(
                            timestamp__gte=some_day_last_week,
                            timestamp__lte=timezone.now(),
                            action_object_content_type=doctype)
                        for item in all_content:
                            if item.action_object_object_id in content_id_set:
                                continue
                            content_id_set.append(item.action_object_object_id)
                            display_items.append(item)
                elif ctype == member_ct:
                    # this *should* be temporary until we have an action
                    # for when a member joins a group. Until then, just
                    # show all new members
                    cxt_label = 'users'
                    members = Action.objects.filter(
                        timestamp__gte=some_day_last_week,
                        timestamp__lte=timezone.now(),
                        action_object_content_type=ctype)
                    for member in members:
                        display_items.append(member)
                else:
                    content_id_set = []
                    cxt_label = ctype.model
                    all_content = user.get_activity_stream().filter(
                        timestamp__gte=some_day_last_week,
                        timestamp__lte=timezone.now(),
                        action_object_content_type=ctype)
                    for item in all_content:
                        if item.action_object_object_id in content_id_set:
                            continue
                        content_id_set.append(item.action_object_object_id)
                        if ctype.model == 'threadedcomment':
                            if not item.action_object.title:
                                comments.append(item)
                                continue
                        # only include live case reports
                        if ctype.model == 'casereport' and item.action_object.workflow_state != 'live':
                            continue
                        display_items.append(item)
                results += len(display_items)
                sorted_items = sorted(
                    display_items,
                    key=lambda c: c.timestamp,
                    reverse=True,
                )
                email_context.update({cxt_label: sorted_items})

            from collections import Counter
            comment_parents = []
            for comment in comments:
                cid = comment.action_object_object_id
                parent = ThreadedComment.objects.get(pk=cid).content_object
                while parent._meta.model_name == 'threadedcomment':
                    # keep going up until we're at the top level item
                    parent = parent.content_object
                comment_parents.append(parent)
            commentcounter = Counter(comment_parents)
            email_context.update({'all_comments': commentcounter})
            for comment in commentcounter:
                # ctype = comment._meta.model_name
                ctype = 'document'
                if ctype == 'link' or ctype == 'file' or ctype == 'image':
                    ctype = 'document'
                try:
                    email_context[ctype].append(comment)
                except:
                    import pdb; pdb.set_trace()
                    continue
            if not results:
                continue
            template = 'emails/weekly_summary'
            message_body = render_to_string('{}.txt'.format(template), email_context)
            mail = EmailMessage(subject, message_body,
                                settings.DEFAULT_FROM_EMAIL,
                                [user.email])
            mail.content_subtype = "html"
            mail.send()
