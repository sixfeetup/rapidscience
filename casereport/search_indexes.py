__author__ = 'yaseen'

from django.template.loader import render_to_string

from haystack import indexes

from rlp.search.search_indexes import TaggableBaseIndex
from casereport.havoc_interface import get_all_synonyms

from .models import CaseReport, ResultValueEvent
from .models import TestEvent
from .models import TreatmentEvent
from .models import DiagnosisEvent


class CaseReportIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='title')
    primary_author = indexes.CharField(faceted=True)
    workflow_state = indexes.CharField(faceted=True)
    gender = indexes.CharField(model_attr='gender', faceted=True)
    age = indexes.IntegerField(model_attr='age', faceted=True)
    abberations = indexes.CharField(faceted=True)
    pub_or_mod_date = indexes.DateTimeField(model_attr='sort_date')
    treatment_type = indexes.MultiValueField(faceted=True)
    country = indexes.MultiValueField(faceted=True)
    # I believe suggestions is an incomplete implementation
    # that was going to be based upon this:
    # https://www.egrovesys.com/blog/solr-implementation-using-django-haystack/
    suggestions = indexes.FacetCharField()

    def get_model(self):
        return CaseReport

    def prepare(self, obj):
        prepared_data = super(CaseReportIndex, self).prepare(obj)

        # FacetCharFields are limited to 32k chars after encoding.
        suggestions_text = prepared_data['text']\
            .encode('utf-8').decode('ascii', 'ignore')[:32765]
        prepared_data['suggestions'] = suggestions_text

        return prepared_data

    def index_queryset(self, using=None):
        cases = CaseReport.objects.all()
        if using == 'casescentral':
            return cases
        else:
            return cases.filter(workflow_state='live')

    def prepare_text(self, obj):
        # synonyms = self.get_synonyms(obj)
        reported_date = obj.get_reported_date()
        treatment_names = self.prepare_treatments(obj)
        searchstring = render_to_string(
            'casereport/search/indexes/casereport/casereport_text.txt',
            {'object': obj,
             'reported_date': reported_date,
             'treatment_names': treatment_names})


        return searchstring

    def prepare_primary_author(self, obj):
        return obj.primary_author.pk

    def prepare_country(self, obj):
        author = obj.primary_author
        if author.institution:
            return [author.institution.country]
        return None

    def prepare_treatments(self, obj):
        events = obj.get_treatments()
        treatments = {i.name.strip().capitalize() for i in events}
        treatments = list(treatments)
        return treatments

    def prepare_workflow_state(self, obj):
        # Haystack doesn't seem to read directly from an FSMField
        return obj.workflow_state

    def get_synonyms(self, obj):
        terms = []
        mols = obj.molecular_abberations.all()
        tests = TestEvent.objects.filter(casereport_f=obj)
        treatments = TreatmentEvent.objects.filter(casereport_f=obj)
        diagnosis = DiagnosisEvent.objects.filter(casereport_f=obj)
        for mol in mols:
            terms.append(mol.name)
        for test in tests:
            terms.append(test.name)
            terms.append(test.body_part)
            terms.append(test.specimen)
        for treat in treatments:
            if treat.side_effects:
                terms.extend(treat.side_effects.split(','))
            terms.append(treat.name)
            terms.append(treat.outcome)
            terms.append(treat.treatment_type)
        for digo in diagnosis:
            if digo.symptoms:
                terms.extend(digo.symptoms.split(','))
            terms.append(digo.name)
            terms.append(digo.specimen)
            terms.append(digo.body_part)
        terms = {_f for _f in terms if _f}
        terms = list(terms)
        term_string = ','.join(terms)
        synonyms = get_all_synonyms(terms=term_string)
        return synonyms

    def prepare_treatment_type(self, obj):
        events = obj.get_treatments()
        return [i.treatment_type for i in events]

    def get_outcomes(self, obj):
        events = TreatmentEvent.objects.filter(casereport_f=obj)
        outcomes = []
        for e in events:
            outcomes.append(e.outcome)
        return outcomes

    def get_results(self, obj):
        events = ResultValueEvent.objects.filter(test__casereport_f=obj)
        results = []
        for e in events:
            results.append(e.value)
        return results
