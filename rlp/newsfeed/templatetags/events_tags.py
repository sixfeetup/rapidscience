from django import template

register = template.Library()


@register.inclusion_tag(
    'newsfeed/_events.html',
    takes_context=True
)
def show_events_hero(context):
    from rlp.events.models import Event
    event = Event.objects.last()
    return {
        'event': event,
        'request': context['request'],
    }