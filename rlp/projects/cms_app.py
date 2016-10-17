from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from .cms_menus import ProjectMenu


class ProjectApp(CMSApp):
    name = "Projects"
    urls = ["rlp.projects.urls"]
    app_name = "projects"
    menus = [ProjectMenu]


apphook_pool.register(ProjectApp)
