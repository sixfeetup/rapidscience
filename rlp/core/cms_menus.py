from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _


anon = {'visible_for_anonymous': True}  # allow anonymous
auth = {'visible_for_anonymous': False}  # require authentication


class MainNavigation(Menu):

    def get_nodes(self, request):
        return [
            NavigationNode(_('Dashboard'), '/dashboard/', 1, attr=auth),
            NavigationNode(_('About'), '/about/', 2, attr=anon),
            NavigationNode(_('Search'), '/search/', 3, attr=auth),
            NavigationNode(_('Groups'), '/groups/', 4, attr=anon),
            NavigationNode(_('Cases Central'), '/casereport/', 5, attr=auth),
        ]

menu_pool.register_menu(MainNavigation)
