from django.contrib.sites.shortcuts import get_current_site
from django import template

register = template.Library()


@register.inclusion_tag(
    'cms/homepage_events.html',
    takes_context=True
)
def homepage_events(context):
    from rlp.events.models import Event
    event = Event.objects.last()
    return {
        'event': event,
        'request': context['request'],
    }

@register.inclusion_tag(
    'djangocms_blog/blog_widget.html',
    takes_context=True
)
def blog_widget(context):
    from djangocms_blog.models import Post
    posts = Post.objects.published()[:2]
    return {
        'posts': posts,
        'request': context['request'],
        'site': get_current_site(context['request']),
    }
