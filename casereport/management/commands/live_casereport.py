__author__ = 'nadeemaslam'

from datetime import datetime
from datetime import timedelta
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core import management
from django.core.management.base import BaseCommand
from casereport.models import CaseReport
from casereport.constants import WorkflowState


class Command(BaseCommand):
    help = 'posting of approved case reports to live site using update solr command'

    def handle(self, *args, **options):
        prev_day = datetime.today() - timedelta(1)
        casereports = CaseReport.objects.filter(modified_on__gte=prev_day,
                                                workflow_state=WorkflowState.LIVE)
        self.reindexsolr()
        for case in casereports:
            self.live_case_mail(case)

    def reindexsolr(request):
        management.call_command('update_index', interactive=False)


    def live_case_mail(self, case):
        Headers = {'Reply-To': settings.SERVER_EMAIL}
        recipient = []
        authorized_recipient = []
        for author in case.authorized_reps.all():
            authorized_recipient.append(str(author))
        for phy in case.referring_physician.all():
            recipient.append(str(phy.email))
        message = render_to_string('live_case_email.html', {'recipient': case.referring_physician.all(),
                                                            'title': case.title,
                                                            'id': case.id,
                                                            'DOMAIN': settings.DOMAIN})
        msg = EmailMessage(settings.CASE_LIVE, message, settings.SERVER_EMAIL, recipient,
                           headers=Headers, cc=authorized_recipient, bcc=settings.BCC_LIST)
        msg.content_subtype = "html"
        msg.send()
