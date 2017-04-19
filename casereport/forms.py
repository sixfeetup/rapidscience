__author__ = 'yaseen'

from collections import defaultdict
from haystack.forms import FacetedSearchForm

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


class MultiFacetedSearchForm(FacetedSearchForm):

    def search(self):
        # sqs = super(FacetedSearchForm, self).search()
        if not self.is_valid():
            query = 'sarcoma'
        else:
            query = self.cleaned_data.get('q')
        if not query:
            query = 'sarcoma'

        if hasattr(self, 'cleaned_data'):
            sqs = self.searchqueryset.filter(
                content__startswith=self.cleaned_data.get('q'))
        else:
            sqs = self.searchqueryset
        multi_facet = defaultdict(list)

        if self.load_all:
            sqs = sqs.load_all()

        or_search = ['gender', 'country', 'authornot', 'primary_physician']
        facet_primary = [False, '']
        facet_author = [False, '']
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            if 'authornot' in facet:
                idx = facet.replace('authornot:', '')
                facet_author = [True, idx]
            if 'primary_physician' in facet:
                idx = facet.replace('primary_physician:', '')
                facet_primary = [True, idx]

            field, value = facet.split(":", 1)
            if value:
                multi_facet[field].append(value)
                if field == 'age_exact':
                    min_val, max_val = value.strip('[').strip(']').split('TO')
                    sqs = sqs.filter(age__gte=int(min_val), age__lte=int(max_val))
                elif field not in or_search:
                    sqs = sqs.narrow('%s:"%s"' % (field, value))

        if facet_author[0]:
            if not facet_primary[0]:
                sqs = sqs.exclude(primary_physician='{0}'.format(facet_author[1]))
            self.selected_facets.remove('authornot:{0}'.format(facet_author[1]))
        elif facet_primary[0]:
            sqs = sqs.narrow('primary_physician:{0}'.format(facet_primary[1]))
        or_search.remove('primary_physician')
        or_search.remove('authornot')

        for field, values in multi_facet.items():
            if field not in or_search:
                continue
            values = ['"' + sqs.query.clean(v) + '"' for v in values]
            sqs = sqs.narrow(u'{!tag=%s}%s:(%s)' % (
                field.upper(),
                field,
                " OR ".join(values)))
        return sqs

    def get_suggestion(self):
        if not self.is_valid():
            return None
        return self.searchqueryset.auto_query(self.cleaned_data['q']).spelling_suggestion()
