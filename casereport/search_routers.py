import urllib.request
from django.conf import settings
from haystack import routers

from casereport.constants import WorkflowState
from casereport.models import CaseReport


class CaseReportRouter(routers.BaseRouter):
    def for_write(self, **hints):
        obj = hints['instance']
        if check_connection('casescentral'):
            if isinstance(obj, CaseReport):
                return 'casescentral'
        return

    def for_read(self, **hints):
        if check_connection('casescentral'):
            return 'casescentral'
        return 'default'

class GeneralSearchRouter(routers.DefaultRouter):

    def for_write(self, **hints):
        """ Only LIVE casereports in the general search.
        """
        obj = hints['instance']

        if isinstance(obj, CaseReport):
            if obj.workflow_state != WorkflowState.LIVE:
                return

        return 'default'


def check_connection(type):
    url = settings.HAYSTACK_CONNECTIONS[type]['URL']
    try:
        urllib.request.urlopen(url, timeout=1)
        return True
    except urllib.request.URLError:
        pass
    return False
