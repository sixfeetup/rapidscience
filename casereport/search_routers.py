from haystack import routers


class CaseReportRouter(routers.BaseRouter):
    def for_write(self, **hints):
        return 'casescentral'

    def for_read(self, **hints):
        return 'casescentral'
