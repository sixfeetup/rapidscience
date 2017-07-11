import urllib.request
from django.conf import settings
from haystack import routers


class CaseReportRouter(routers.BaseRouter):
    def for_write(self, **hints):
        if check_connection('casescentral'):
            return 'casescentral'
        return 'default'

    def for_read(self, **hints):
        if check_connection('casescentral'):
            return 'casescentral'
        return 'default'


def check_connection(type):
    url = settings.HAYSTACK_CONNECTIONS[type]['URL']
    try:
        urllib.request.urlopen(url, timeout=1)
        return True
    except urllib.request.URLError:
        pass
    return False
