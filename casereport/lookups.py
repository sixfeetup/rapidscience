from ajax_select import register, LookupChannel
from .havoc_interface import havoc_results

from casereport.models import DiagnosisEvent
from casereport.models import MolecularAbberation
from casereport.models import TestEvent
from casereport.models import TreatmentEvent

__author__ = 'asreedh'


class BaseLookup(LookupChannel):

    def get_query(self, q, request):
        query = q.split(', ')[-1]
        vocab = 'nci'
        if 'molecularabberation' in request.META['HTTP_REFERER']:
            vocab = 'hgnc'
        results = havoc_results(api='concepts', vocab=vocab, term=query+'%', partial=True)
        return results[:10]

    def format_item_display(self, obj):
        return "<span class='tag'>%s</span>" % obj['value']

    def format_match(self, obj):
        return obj['value']

    def get_value(self, obj):
        return '%s' %(obj['value'])

    def get_result(self, obj):
        return '%s' %(obj['value'])


@register('name')
@register('specimen')
@register('symptoms')
class DiagnosisEventLookup(BaseLookup):
    model = DiagnosisEvent

@register('name')
@register('specimen')
@register('symptoms')
class DiagnosisEventLookup(BaseLookup):
    model = DiagnosisEvent


@register('molecularabberation')
class MolecularAbberationLookup(BaseLookup):
    model = MolecularAbberation


@register('name')
@register('specimen')
@register('body_part')
class TestEventLookup(BaseLookup):
    model = TestEvent


@register('side_effects')
@register('name')
# @register('treatment_type')
@register('outcome')
class TreatmentEventLookup(BaseLookup):
    model = TreatmentEvent
