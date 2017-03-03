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


class SetVarNode(template.Node):
    def __init__(self, new_val, var_name):
        self.new_val = new_val
        self.var_name = var_name


    def render(self, context):
        if self.new_val[0] == self.new_val[-1] and self.new_val[0] in ('"', "'"):
            context[self.var_name] = self.new_val
        else:
            try:
                #context[self.var_name] = template.resolve_variable(self.new_val,context)
                #context[self.var_name] = self.new_val.resolve(context)
                # TODO: for shame.    Find a better way!!!
                from django.template import Template
                val = Template( "{{" + self.new_val + "}}")
                context[self.var_name] = val.render(context)
            except Exception as e:
                return "failed to resolve:" + self.new_val + " -- " + str(e)
        return ''

import re
@register.tag
def setvar(parser,token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError( "%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError( "%r tag had invalid arguments" % tag_name )
    new_val, var_name = m.groups()
    #if not (new_val[0] == new_val[-1] and new_val[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError( "%r tag's argument should be in quotes" % tag_name )
    #return SetVarNode(new_val[1:-1], var_name)
    return SetVarNode(new_val, var_name)
