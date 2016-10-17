from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class NewsFeedApp(CMSApp):
    name = "News Feed"
    urls = ["rlp.newsfeed.urls"]
    app_name = "newsfeed"


apphook_pool.register(NewsFeedApp)
