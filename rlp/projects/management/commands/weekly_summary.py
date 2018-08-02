from collections import Counter
from datetime import timedelta
import html2text
import sys

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from actstream.models import Action

from rlp.accounts.models import User
from rlp.core.utils import can_send_email
from rlp.discussions.models import ThreadedComment
from rlp.projects.models import Project


class Command(BaseCommand):
    """ Sends a weekly summary of site activity.
        Should only be run once per week.
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Specify a list of emails',
        )

    def handle(self, *args, **options):
        emails = options.get('to')
        if emails:
            users = User.objects.filter(email__in=emails.split(','))
            self.process(users)
        else:
            users = User.objects.filter(is_active=True)
            # globally_enabled = users.filter(digest_prefs='disabled') # si weekle
            # vv users who haven't set group preference, or who hasn't set it to 'digest'
            enabled_for_groups = users.filter(
                projectmembership__digest_prefs='enabled').distinct('id')

            globally_enabled = users.filter(digest_prefs='enabled').exclude(
                id__in=[u.id for u in enabled_for_groups])  # si weekly
            # It's important to note that those are merely candidates to receive
            # a digest.
            try:
                print("sending {} to those enabled_for_groups".format(
                    enabled_for_groups.count()))
                self.process(enabled_for_groups)

                print("sending {} to those globally_enabled".format(
                    globally_enabled.count()))
                self.process(globally_enabled)

            except Exception as err:
                subject = "{}".format(sys.argv[1])
                message = "{}".format(err)
                mail_admins(subject, message)
                raise

    def process(self, users):
        # unfortunately that includes users who enabled the digest,
        # but disabled the digest for all of the groups in their digest.

        some_day_last_week = timezone.now() - timedelta(days=7)
        year, week, day = some_day_last_week.isocalendar()
        # define the content types
        project_ct = ContentType.objects.get(app_label='projects',
                                             model='project')

        user_ct = ContentType.objects.get(app_label='accounts',
                                          model='user')

        casereport_ct = ContentType.objects.get(app_label='casereport',
                                                model='casereport')
        comment_ct = ContentType.objects.get(app_label='discussions',
                                             model='threadedcomment')
        biblio_ct = ContentType.objects.get(app_label='bibliography',
                                            model='userreference')
        docs_cts = ContentType.objects.filter(app_label='documents')
        member_ct = ContentType.objects.get(model='user')
        subject = "Weekly summary of new activity"

        # using users with group digests settings enabled,
        # or global digests enabled, but no group digests enabled
        # if any of the groups have direct or none,
        # then those groups need to be filtered out.

        for user in users:  # everybody who MIGHT get the digest
            projects = user.get_digest_projects()
            if not projects.count():
                print("skipping user_id {} because they have no active digest"
                      " subscriptions".format(user.id))
                continue
            activity_stream = user.get_activity_stream().filter(
                timestamp__gte=some_day_last_week,
                timestamp__lte=timezone.now(),
                target_content_type=project_ct,
                target_object_id__in=[p.id for p in projects],
            )

            email_context = {
                'user': user,
                'site': settings.DOMAIN,
                'user_groups': projects
            }

            results = 0
            comments = []
            # loop through all content returned to strip out duplicates
            # (for when multiple actions happen on one piece of content)
            for ctype in [comment_ct, casereport_ct, docs_cts, biblio_ct, member_ct]:
                display_items = []  # items to display in the email
                # docs_cts has multiple types we group together
                if ctype == docs_cts:
                    cxt_label = 'document'
                    for doctype in docs_cts:
                        content_id_set = []
                        actions = activity_stream.filter(
                            action_object_content_type=doctype)

                        for action in actions:
                            # if type(item.target) == Project:
                            #    if not can_send_email(user, item.target, True):
                            #        continue
                            if action.action_object_object_id in content_id_set:
                                # dedupe
                                continue
                            content_id_set.append(action.action_object_object_id)
                            display_items.append(action)
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
                        if type(member.target) == Project:
                            if not can_send_email(user, member.target, True):
                                continue
                        display_items.append(member)
                else:
                    content_id_set = []
                    cxt_label = ctype.model
                    all_content = activity_stream.filter(
                        action_object_content_type=ctype)

                    for item in all_content:
                        if item.action_object_object_id in content_id_set:
                            continue
                        # if type(item.target) == Project:
                        #    if not can_send_email(user, item.target, True):
                        #        continue
                        content_id_set.append(item.action_object_object_id)
                        if ctype.model == 'threadedcomment':
                            if not item.action_object.title:
                                # handle comments below
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

            # combine comments for the same object
            comment_parents = []
            for comment in comments:
                cid = comment.action_object_object_id
                parent = ThreadedComment.objects.get(pk=cid).content_object
                while parent._meta.model_name == 'threadedcomment':
                    # keep going up until we're at the top level item
                    if parent.content_object._meta.model_name == 'site':
                        break
                    parent = parent.content_object
                ptype = parent._meta.model_name
                if ptype == 'link' or ptype == 'file' or ptype == 'image':
                    ptype = 'document'
                if ptype == 'casereport':
                    type_key = '{0}_comments'.format(ptype)
                else:
                    type_key = 'all_comments'
                comment_obj = comment.action_object
                email_context.setdefault(type_key, []).append((comment_obj, parent))
                comment_parents.append(parent)

            """This section below can be used for displaying one entry for each
               piece of content that had comments in the last week:
               '<x> comments on <item title>'
            """
            # commentcounter = Counter(comment_parents)
            # for comment in commentcounter:
            #     ptype = comment._meta.model_name
            #     if ptype == 'link' or ptype == 'file' or ptype == 'image':
            #         ptype = 'document'
            #     # add to doc type comments
            #     type_key = '{0}_comments'.format(ptype)
            #     email_context.setdefault(type_key, []).append(
            #         (comment, commentcounter[comment]))

            new_projects = Project.objects.filter(created__gte=some_day_last_week)
            # TODO  exclude...
            display_projects = []
            for project in new_projects:
                display_projects.append({
                    'user_is_member': user in project.active_members(),
                    'group': project
                })
            email_context['new_projects'] = display_projects

            if not results and not new_projects and not comments:
                continue
            template = 'emails/weekly_summary'
            html_message = render_to_string(
                '{}.txt'.format(template), email_context)
            text_maker = html2text.HTML2Text()
            text_maker.body_width = 100
            message = text_maker.handle(html_message)

            send_mail(
                subject,
                message,
                settings.WEEKLY_SUMMARY_EMAIL,
                [user.email],
                html_message=html_message,
            )
