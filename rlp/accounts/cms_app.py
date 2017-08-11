from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class DashboardApp(CMSApp):
    name = "Dashboard"
    urls = ["rlp.accounts.urls"]
    app_name = "dashboard"


apphook_pool.register(DashboardApp)
