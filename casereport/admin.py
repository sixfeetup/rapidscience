from ajax_select.fields import AutoCompleteField

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django import forms

from casereport.models import *
from casereport.constants import TREATMENT_TYPES

__author__ = 'yaseen'

Register_models = [
    AuthorizedRep, Institution, ResultValueEvent, CaseReportHistory]

admin.site.register(Register_models)


class TreatmentForm(ModelForm):
    treatment_type = forms.MultipleChoiceField(widget=forms.SelectMultiple(), choices=TREATMENT_TYPES)

    def __init__(self, *args, **kwargs):
        super(TreatmentForm, self).__init__(*args, **kwargs)
        self.fields['treatment_type'] = forms.MultipleChoiceField(widget=forms.SelectMultiple(), choices=TREATMENT_TYPES)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['treatment_type'] = list(instance.treatment_type.split(','))

    class Meta:
        fields = "__all__"
        model = Treatment

    def clean_treatment_type(self):
        treatment_type = self.cleaned_data['treatment_type']
        return ','.join(treatment_type)


class TreatmentInline(admin.StackedInline):
    model = Treatment
    fk_name = 'casereport'
    form = TreatmentForm


class CaseFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'created_on',
                    'casereport')

    def casereport(self, obj):
        if CaseReport.objects.filter(casefile_f=obj).count() > 0:
            link = '<a href="%s">View</a>' % \
                reverse('admin:casereport_casereport_change',
                        args=(obj.casereport.all()[0].id,))
        else:
            link = '<a href="%s?casefile=%s">Convert</a>' \
                % (reverse('admin:casereport_casereport_add'), obj.id)
        return link
    casereport.allow_tags = True
    casereport.short_description = 'Casereport'


class CaseReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'gender', 'age',
                    'status', 'created_on', 'view_casefile')
    order_by = ('created_on',)
    list_filter = ('status',)
    inlines = [
        TreatmentInline,
    ]

    def view_casefile(self, obj):
        if obj.casefile_f:
            link = '<a href="%s">View</a>' % \
                reverse('admin:casereport_casefile_change',
                        args=(obj.casefile_f.id,))
        else:
            link = ''
        return link
    view_casefile.allow_tags = True
    view_casefile.short_description = 'Casefile'


admin.site.register(CaseFile, CaseFileAdmin)
admin.site.register(CaseReport, CaseReportAdmin)


class MolecularAbberationForm(ModelForm):
    molecule = AutoCompleteField('molecularabberation', required=False)

    class Meta:
        fields = "__all__"
        model = TestEvent


class MolecularAbberationAdmin(admin.ModelAdmin):
    form = MolecularAbberationForm

class EventBaseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        case = None
        try:
            case = args[0].get('casereport')
        except Exception as e:
            try:
                case = kwargs['instance'].casereport
            except Exception as e:
                pass
        super(EventBaseForm, self).__init__(*args, **kwargs)
        if case:
            self.fields['previous_event'].queryset = Event.objects.filter(casereport=case)
            self.fields['next_event'].queryset = Event.objects.filter(casereport=case)
            self.fields['parent_event'].queryset = Event.objects.filter(casereport=case, event_type=None)

    def clean_parent_event(self):
        case = self.cleaned_data.get('casereport')
        parent_event = self.cleaned_data.get('parent_event')
        if parent_event:
            if parent_event.casereport != case:
                raise forms.ValidationError("Not a valid parent event")
        return parent_event

    def clean_previous_event(self):
        case = self.cleaned_data.get('casereport')
        previous_event = self.cleaned_data.get('previous_event')
        if previous_event:
            if previous_event.casereport != case:
                raise forms.ValidationError("Not a valid previous event")
        return previous_event

    def clean_next_event(self):
        case = self.cleaned_data.get('casereport')
        next_event = self.cleaned_data.get('next_event')
        if next_event:
            if next_event.casereport != case:
                raise forms.ValidationError("Not a valid next event")
        return next_event



class EventBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_event', 'previous_event', 'next_event')
    list_filter = ('casereport',)
    exclude = ('event_type', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["previous_event", "next_event"]:
            kwargs["queryset"] = Event.objects.all().order_by('-id')
        if db_field.name == "parent_event":
            kwargs["queryset"] = Event.objects.filter(event_type__isnull=True).order_by('-id')
        if db_field.name == "casereport":
            kwargs["queryset"] = CaseReport.objects.all().order_by('-id')
        return super(EventBaseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class EventForm(EventBaseForm):
    pass

    class Meta:
        fields = "__all__"
        model = Event

class EventAdmin(EventBaseAdmin):
    form = EventForm


class TreatmentEventForm(EventBaseForm):
    side_effects = AutoCompleteField('side_effects', required=False)
    name = AutoCompleteField('name')
    # outcome = AutoCompleteField('outcome', required=False)
    treatment_type = forms.MultipleChoiceField(widget=forms.SelectMultiple(), choices=TREATMENT_TYPES)

    class Meta:
        fields = "__all__"
        model = TreatmentEvent

    def __init__(self, *args, **kwargs):
        super(TreatmentEventForm, self).__init__(*args, **kwargs)
        self.fields['treatment_type'] = forms.MultipleChoiceField(widget=forms.SelectMultiple(), choices=TREATMENT_TYPES)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['treatment_type'] = list(instance.treatment_type.split(','))

    def clean_treatment_type(self):
        treatment_type = self.cleaned_data['treatment_type']
        return ','.join(treatment_type)



class TreatmentEventAdmin(EventBaseAdmin):
    form = TreatmentEventForm
    list_display = ('name', 'parent_event', 'previous_event', 'next_event', 'combined_with')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["followed_by", "combined_with"]:
            kwargs["queryset"] = self.model.objects.order_by('-id')
        return super(TreatmentEventAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class DiagnosisEventForm(EventBaseForm):
    name = AutoCompleteField('name')
    specimen = AutoCompleteField('specimen', required=False)
    symptoms = AutoCompleteField('symptoms', required=False)

    class Meta:
        fields = "__all__"
        model = DiagnosisEvent


class DiagnosisEventAdmin(EventBaseAdmin):
    form = DiagnosisEventForm


class TestEventForm(EventBaseForm):
    body_part = AutoCompleteField('body_part', required=False)
    name = AutoCompleteField('name')
    specimen = AutoCompleteField('specimen', required=False)

    class Meta:
        fields = "__all__"
        model = TestEvent


class TestEventAdmin(EventBaseAdmin):
    form = TestEventForm

class PhysicianAdmin(admin.ModelAdmin):
    list_display = ('name', 'affiliation', 'city', 'country')
    list_filter = ('affiliation', 'affiliation__city', 'affiliation__country')

    def country(self, obj):
        if obj.affiliation:
            return obj.affiliation.country.name
        else:
            return None
    country.allow_tags = True
    country.short_description = 'Country'

    def city(self, obj):
        if obj.affiliation:
            return obj.affiliation.city
        else:
            return None
    city.allow_tags = True
    city.short_description = 'City'


admin.site.register(MolecularAbberation, MolecularAbberationAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(TreatmentEvent, TreatmentEventAdmin)
admin.site.register(TestEvent, TestEventAdmin)
admin.site.register(DiagnosisEvent, DiagnosisEventAdmin)
admin.site.register(Physician, PhysicianAdmin)
