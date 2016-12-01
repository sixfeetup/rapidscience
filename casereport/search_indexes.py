from casereport.havoc_interface import  get_all_synonyms

__author__ = 'yaseen'
from django.template.loader import render_to_string

from haystack import indexes
from .models import CaseReport, ResultValueEvent
from .models import TestEvent
from .models import TreatmentEvent
from .models import DiagnosisEvent

class CaseReportIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='title')
    gender = indexes.CharField(model_attr='gender', faceted=True)
    age = indexes.IntegerField(model_attr='age', faceted=True)
    molecular_abberations = indexes.MultiValueField(faceted=True)
    molecules = indexes.MultiValueField(faceted=True)
    treatments = indexes.MultiValueField(faceted=True)
    cr_tests = indexes.MultiValueField(faceted=True)
    created_on = indexes.DateTimeField(model_attr='created_on')
    modified_on = indexes.DateTimeField(model_attr='modified_on')
    treatment_type = indexes.MultiValueField(faceted=True)
    country = indexes.MultiValueField(faceted=True)

    def get_model(self):
        return CaseReport

    def index_queryset(self, using=None):
        cases = CaseReport.objects.filter(status='approved')
        return cases

    def prepare_text(self, obj):
        synonyms = self.get_synonyms(obj)
        reported_date = obj.get_reported_date()
        outcomes = self.get_outcomes(obj)
        results = self.get_results(obj)
        test_names = self.prepare_cr_tests(obj)
        treatment_names = self.prepare_treatments(obj)
        searchstring = render_to_string('search/indexes/casereport/casereport_text.txt',
                                {'object': obj, 'synonyms': synonyms,'outcomes':outcomes,'results':results,
                                'reported_date': reported_date,'test_names':test_names,'treatment_names':treatment_names})
        return searchstring

    def prepare_country(self, obj):
        physician = obj.primary_physician
        return [physician.get_country()]

    def prepare_molecular_abberations(self, obj):
        names = obj.molecular_abberations.all()
        names = [i for i in names]
        return names

    def prepare_molecules(self, obj):
        mols = obj.molecular_abberations.all()
        molecules = [i.molecule for i in mols]
        return molecules

    def prepare_treatments(self, obj):
        events = obj.event_set.filter(event_type='treatment')
        treatments = [i.name.strip().capitalize() for i in events]
        treatments = list(set(treatments))
        return treatments

    def prepare_cr_tests(self, obj):
        events = obj.event_set.filter(event_type='test')
        tests = [i.name.strip().capitalize() for i in events]
        tests = list(set(tests))
        return tests

    def get_synonyms(self, obj):
        terms = []
        mols = obj.molecular_abberations.all()
        tests = TestEvent.objects.filter(casereport=obj)
        treatments = TreatmentEvent.objects.filter(casereport=obj)
        diagnosis = DiagnosisEvent.objects.filter(casereport=obj)
        for mol in mols:
            terms.append(mol.molecule)
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
        terms = [_f for _f in terms if _f]
        terms = list(set(terms))
        term_string = ','.join(terms).encode('utf-8')
        synonyms = get_all_synonyms(terms=term_string)
        return synonyms

    def prepare_treatment_type(self,obj):
        treatments = TreatmentEvent.objects.filter(casereport=obj)
        types = [i.treatment_type.strip().capitalize() for i in treatments]
        types = list(set(types))
        return types

    def get_outcomes(self, obj):
        events = TreatmentEvent.objects.filter(casereport=obj)
        outcomes = []
        for e in events:
            outcomes.append(e.outcome)
        return outcomes

    def get_results(self, obj):
        events = ResultValueEvent.objects.filter(test__casereport=obj)
        results = []
        for e in events:
            results.append(e.value)
        return results



