from django import template

register = template.Library()


@register.inclusion_tag(
    'newsfeed/_news_widget.html',
    takes_context=True
)
def show_news_items(context):
    from rlp.newsfeed.models import NewsItem
    return {
        'objects': NewsItem.published.all()[:3],
        'request': context['request'],
    }
