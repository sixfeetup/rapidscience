from django.conf import settings

from haystack.forms import SearchForm


def google_analytics(request):
    context = {}
    if not settings.DEBUG and hasattr(settings, 'GOOGLE_UA'):
        context['GOOGLE_UA'] = settings.GOOGLE_UA
    return context


def search_form(request):
    context = {
        'search_form': SearchForm()
    }
    return context
