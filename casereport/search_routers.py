import urllib.request
from django.conf import settings
from haystack import routers

import casereport.search_indexes
from casereport.constants import WorkflowState
from casereport.models import CaseReport
from rlp.discussions.models import ThreadedComment


class CaseReportRouter(routers.BaseRouter):
    def for_write(self, **hints):
        try:
            obj = hints['instance']
            if not check_connection('casescentral'):
                return 'default'
            if isinstance(obj, CaseReport):
                if obj.workflow_state == WorkflowState.LIVE:
                    return ['default', 'casescentral']
                return 'casescentral'
            elif isinstance(obj, ThreadedComment):
                if obj.is_editorial_note:
                    return None
                elif obj.is_removed:
                    return None
                elif not obj.is_public:
                    return None

        except KeyError as no_instance:
            index = hints['index']
            if isinstance(index, casereport.search_indexes.CaseReportIndex):
                return 'casescentral'
        return 'default'

    def for_read(self, **hints):
        if check_connection('casescentral'):
            return 'casescentral'
        return 'default'


class GeneralSearchRouter(routers.DefaultRouter):

    def for_write(self, **hints):
        """ Only LIVE casereports in the general search.
        """
        if check_connection('casescentral'):
            return
        try:
            obj = hints['instance']

            if isinstance(obj, CaseReport):
                if obj.workflow_state != WorkflowState.LIVE:
                    return 'default'
        except KeyError as no_instance:
            pass
            # not sure how to exclude non-live casereports here.
        return 'default'


def check_connection(type):
    url = settings.HAYSTACK_CONNECTIONS[type]['URL']
    url = url.replace("solr/c", "solr/#/c")
    try:
        urllib.request.urlopen(url, timeout=1)
        return True
    except urllib.request.URLError:
        pass
    return False
