from django.conf import settings
from django.contrib.sites.models import Site

from cms.menu_bases import CMSAttachMenu
from cms.templatetags.cms_tags import _get_page_by_untyped_arg
from menus.base import Menu, Modifier, NavigationNode
from menus.menu_pool import menu_pool


from .models import Project, Topic


class ProjectMenu(CMSAttachMenu):
    name = "Group Menu"

    def get_nodes(self, request):
        nodes = []
        menu_id = 1000
        page = _get_page_by_untyped_arg('project-landing', request, settings.SITE_ID)
        nodes.append(NavigationNode(
            'Groups Overview',
            page.get_absolute_url(),
            page.id
        ))
        for project in Project.objects.filter(topic__isnull=True):
            # the menu tree consists of NavigationNode instances
            # Each NavigationNode takes a label as its first argument, a URL as
            # its second argument and a (for this tree) unique id as its third
            # argument.
            node = NavigationNode(
                project.title,
                project.get_absolute_url(),
                menu_id
            )
            nodes.append(node)
            menu_id += 1
        for topic in Topic.objects.all():
            node = NavigationNode(
                topic.title,
                '',
                menu_id
            )
            nodes.append(node)
            menu_id += 1
            for project in topic.project_set.all():
                node = NavigationNode(
                    project.title,
                    project.get_absolute_url(),
                    menu_id
                )
                nodes.append(node)
                menu_id += 1
        return nodes

menu_pool.register_menu(ProjectMenu)


if settings.SITE_PREFIX == 'chci':
    class SummerInstituteMenu(CMSAttachMenu):
        name = 'Summer Institutes Menu'

        def get_nodes(self, request):
            nodes = list()
            if not request.user.is_authenticated():
                return nodes
            for project in Project.objects.filter(topic__title__iexact='Summer Institutes'):
                node = NavigationNode(
                    project.title,
                    project.get_absolute_url(),
                    2000 + project.id
                )
                nodes.append(node)
            return nodes

    menu_pool.register_menu(SummerInstituteMenu)

