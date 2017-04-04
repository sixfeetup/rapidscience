__author__ = 'yaseen'

from haystack.forms import SearchForm

from django import forms

from rlp.core.forms import MemberListField, GroupListField
from rlp.projects.forms import CommaSeparatedEmailField


class CaseForm(forms.Form):
    members = MemberListField(
        label='Invite Members',
        help_text='Separate names with commas',
        choices=(),  # gets filled in by the view
        required=False,
    )
    external = CommaSeparatedEmailField(
        label='Invite Non-members',
        help_text='Enter institutional e-mails; separate with commas',
        max_length=400,
        required=False,
    )
    groups = GroupListField(
        label='Invite My Groups',
        help_text='Separate names with commas',
        choices=(),  # gets filled in by the view
        required=False,
    )
    invitation_message = forms.CharField(
        max_length=600,
        widget=forms.Textarea,
        required=False,
    )


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
                    sqs = sqs.narrow('%s:"%s"' % (field, value))
        return sqs

    def get_suggestion(self):
        if not self.is_valid():
            return None
        return self.searchqueryset.auto_query(self.cleaned_data['q']).spelling_suggestion()
