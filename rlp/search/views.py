from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from haystack.generic_views import SearchView as BaseSearchView

from .forms import ModelSearchForm


class SearchView(BaseSearchView):
    form_class = ModelSearchForm

    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """A very regrettable override to disable pagination on search results so this will work with
        endless pagination.
        It blends the get_context_data from ContextMixin and MultipleObjectMixin (Django's built-in mixins)
        """
        # From ContextMixin
        if 'view' not in kwargs:
            kwargs['view'] = self
        # MultipleObjectMixin
        queryset = kwargs.pop('object_list', self.object_list)
        context_object_name = self.get_context_object_name(queryset)
        context = {
            'object_list': queryset
        }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        # Override to actually add functionality
        get_request = self.request.GET.dict()
        utf8_get_dict = {
            key: str(val).encode('utf-8')
            for key, val in get_request.items()
        }
        utf8_get_dict.pop('page', '')
        context['query_string'] = urlencode(utf8_get_dict)
        return context

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        This is overridden from the base implementation so we can override the template for endless pagination.
        """
        if self.request.is_ajax():
            self.template_name = 'search/_results.html'
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
