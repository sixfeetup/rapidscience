from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rlp.core.utils import CREATION_VERBS

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


class SiteNode(template.Node):
    def __init__(self, var_name, site):
        self.var_name = var_name
        self.site = site

    def render(self, context):
        context[self.var_name] = self.site
        return ""


@register.tag
def get_current_site_as(parser, token):
    """ load the current site, as defined by settings.SITE_ID into the context.
        useful for templates that don't have access to a request, like for email.

        Use like:
            {% get_current_site_as thesite %}
            {{ thesite.domain }}
    """
    current_site = Site.objects.get_current()
    return SiteNode(token.contents.split()[1], current_site)


@register.simple_tag
def display_tag_links( tagged_item ):
    """ collate all of the Taggit.Tag and managedtags.ManagedTag for the item
        and display them as links to search
    """
    all_tags = {}
    # mtags first, so that tags will replace them if present
    if hasattr(tagged_item, "mtags"):
        for tag in tagged_item.mtags.exclude(slug=''):
            all_tags[tag.slug] = tag
    if hasattr(tagged_item, "tags"):
        for tag in tagged_item.tags.all():
            all_tags[tag.slug] = tag

    sorted_tags = sorted(all_tags.values(), key=lambda x:x.slug)
    return mark_safe(
        render_to_string("core/tag_links.html", {'tags':sorted_tags}))


@register.simple_tag
def display_shared_with(item, user=None):
    # Display 'Shared with...' text if shared with more than the current user
    try:
        viewers = item.get_viewers()
    except AttributeError as not_a_sharable:
        viewers = []
        print("item was not a viewable")


    vlist = []
    for v in viewers:
        # suppress shares by the author to themselves
        if hasattr(item, "user") and v == item.user:
            continue
        if v._meta.model_name == "user":
            url = reverse('profile', args=[v.id])
            vlist.append('<a href="{0}">{1}</a>, '.format(url, v))
        elif v._meta.model_name == "project":
            if (v.approval_required and user in v.active_members()) or \
                    not v.approval_required:
                url = reverse('projects:projects_detail', args=[v.id, v.slug])
                vlist.append('<a href="{0}">{1}</a>, '.format(url, v))
            else:
                vlist.append('{0}, '.format(v))
        else:
            vlist.append('{0}, '.format(v))
    if vlist:
        # cut off the trailing ", " from the last item
        vlist[-1] = vlist[-1][:-2]
        if len(vlist) > 1:
            # replace the oxford comma from the second to last
            vlist[-2] = vlist[-2][:-2]
            vlist.insert(-1, ' and ')

        combined_viewers = "".join(vlist)
        return mark_safe('Shared with {0}'.format(combined_viewers))
    else:
        return ''

@register.filter(needs_autoescape=True)
def link(obj, extra='', autoescape=True):
    """ Emit an html anchor for the passed object.
        Use extra for class, id, or other attributes.
        ex.
            {{ user|link:'class="userlinks" id="myid"' }}

        nb: the careful nesting of quotes.
    """
    if not obj:
        return mark_safe("<!-- {obj} -->".format(obj=obj))
    try:
        res = """<a href="{url}" {extra} >{obj}</a>""".format( url=obj.get_absolute_url(), extra=extra, obj=obj)
        return mark_safe( res )
    except AttributeError as not_linkable:
        return mark_safe(str(obj))


@register.simple_tag
def toggle_bookmark_url(content, viewer):
    if content.is_bookmarked_to(viewer):
        return reverse('remove_bookmark')
    return reverse('bookmark_content')

@register.filter
def verb_alias(verb):
    if verb in CREATION_VERBS:
        return 'posted'
    return verb

@register.simple_tag(takes_context=True)
def user_can_link(context, shared_object ):
    user = context['request'].user
    project = context.get('project', False)
    if project:
        if user in project.active_members():
            return True
    else:
        return True
    return False
