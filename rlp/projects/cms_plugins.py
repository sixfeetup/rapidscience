from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from .models import Topic


class ProjectsPlugin(CMSPluginBase):
    model = CMSPlugin
    name = 'Projects listing'
    render_template = "cms/_projects.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        topics = Topic.objects.all()
        context['topics'] = topics
        return context

plugin_pool.register_plugin(ProjectsPlugin)
