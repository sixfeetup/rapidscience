__author__ = 'yaseen'

from captcha.fields import CaptchaField
from haystack.forms import SearchForm

from django import forms


class CaptchaForm(forms.Form):
    captcha = CaptchaField()


class FacetedSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        self.selected_facets = kwargs.pop("selected_facets", [])
        super(FacetedSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        # sqs = super(FacetedSearchForm, self).search()
        if not self.is_valid():
            query = 'sarcoma'
        else:
            query = self.cleaned_data.get('q')
        if not query:
            query = 'sarcoma'

        sqs = self.searchqueryset.auto_query(query)

        if self.load_all:
            sqs = sqs.load_all()

        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)
            if value:
                if field == 'age_exact':
                    min_val, max_val = value.strip('[').strip(']').split('TO')
                    sqs = sqs.filter(age__gte=int(min_val), age__lte=int(max_val))
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, value))
        return sqs

    def get_suggestion(self):
        if not self.is_valid():
            return None
        return self.searchqueryset.auto_query(self.cleaned_data['q']).spelling_suggestion()
