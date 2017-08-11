from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class CasesCentralApp(CMSApp):
    name = "Cases Central"
    urls = ["casereport.urls"]
    app_name = "crdb"


apphook_pool.register(CasesCentralApp)
