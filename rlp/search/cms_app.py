from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class SearchApp(CMSApp):
    name = "Search"
    urls = ["rlp.search.urls"]
    app_name = "search"


apphook_pool.register(SearchApp)
