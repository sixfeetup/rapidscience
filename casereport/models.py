from access_tokens import tokens
from casereport.constants import GENDER
from casereport.constants import SARCOMA_TYPE
from casereport.constants import STATUS
from casereport.constants import CASE_STATUS
from casereport.constants import TYPE
from casereport.constants import TREATMENT_TYPES
from casereport.constants import PERFORMANCE_STATUS
from casereport.constants import OBJECTIVE_RESPONSES
from casereport.constants import INDEXES
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField
from django.db import models
from django.template.defaultfilters import slugify
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
__author__ = 'yaseen'


class CRDBBase(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class Institution(CRDBBase):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = CountryField()
    address = models.TextField()

    def __unicode__(self):
        return self.name


class Physician(CRDBBase):
    affiliation = models.ForeignKey(Institution, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __unicode__(self):
        return str(self.name) or ''

    def get_name(self):
        return self.name

    def get_country(self):
        if self.affiliation:
            return self.affiliation.country.name.capitalize()
        return None

    def get_country_code(self):
        if self.affiliation:
            return self.affiliation.country.code
        return None


class CaseFile(CRDBBase):
    # referring_physician = models.ForeignKey(Physician, null=True, blank=True)
    name = models.CharField(max_length=200)
    document = models.FileField()

    def __str__(self):
        return self.name.encode('utf-8')

class MolecularAbberation(CRDBBase):
    name = models.CharField(max_length=255)
    molecule = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Genetic Aberration'
        verbose_name_plural = 'Genetic Aberrations'

    def __unicode__(self):
        return '%s: %s' %(self.molecule, self.name)


class AuthorizedRep(CRDBBase):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.email.encode('utf-8')

    def get_name(self):
        return self.email

class CaseReport(CRDBBase):
    title = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    primary_physician = models.ForeignKey(Physician, related_name='primary_case')
    referring_physician = models.ManyToManyField(Physician, null=True, blank=True)
    authorized_reps = models.ManyToManyField(AuthorizedRep, null=True, blank=True)
    sarcoma_type = models.CharField(max_length=100, choices=sorted(SARCOMA_TYPE),null=True, blank=True)
    other_sarcoma_type = models.CharField(max_length=200, null=True, blank=True)
    molecular_abberations = models.ManyToManyField(MolecularAbberation, null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    precision_treatment = models.TextField(null=True, blank=True)
    specimen_analyzed = models.TextField(null=True, blank=True)
    additional_comment = models.TextField(null=True, blank=True)
    previous_treatments = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default='processing')
    casefile = models.ForeignKey(CaseFile, null=True, blank=True)
    index = models.IntegerField(max_length=1, choices=INDEXES, null=True, blank=True)
    pathology = models.TextField(null=True, blank=True)
    progression = models.CharField(max_length=250, null=True, blank=True)
    response = models.CharField(max_length=2, choices=OBJECTIVE_RESPONSES, null=True, blank=True)
    tumor_location = models.CharField(max_length=200,null=True,blank=True)
    molecular_abberations.verbose_name = 'Genetic Aberrations'

    def __str__(self):
        return self.title if self.title else '---'

    def save(self, *args, **kwargs):
        if self.status == CASE_STATUS['E'] or self.status == CASE_STATUS['P']:
            # sending a notify email to admin
            self.notify_admin()
        if self.status == CASE_STATUS['R'] or self.status == CASE_STATUS['A']:
            # sending review email to authorized rep/physicain
            self.send_review_mail()
        super(CaseReport, self).save(*args, **kwargs)

    def notify_admin(self):
        subject = settings.NEW_CASE
        if self.status == CASE_STATUS['E']:
            subject = settings.EDITED
        message_body = render_to_string('admin_notify.html', {'title': self.title,
                                                              'status': self.status,
                                                              'name': self.primary_physician.name})
        recipient_members = settings.DATA_SCIENCE_TEAM
        for member in recipient_members:
            message = EmailMessage(subject, message_body, settings.SERVER_EMAIL, [member])
            message.content_subtype = 'html'
            message.send()

    def send_review_mail(self):
        history_obj = CaseReportHistory.objects.filter(case=self.id).last()
        token = tokens.generate(scope=(), key=self.id, salt=settings.TOKEN_SALT)
        Headers = {'Reply-To': settings.SERVER_EMAIL}
        recipients = list(self.authorized_reps.all())
        primary_recipient = self.primary_physician
        subject = settings.CASE_READY_SUBJECT
        if self.status == CASE_STATUS['R'] and not history_obj:
            for recipient in recipients:
                if recipient.email:
                    message = render_to_string('email_to_authorized.html',
                                               {'id': self.id,
                                                'title': self.title,
                                                'name': recipient.get_name(),
                                                'token': token,
                                                'DOMAIN': settings.DOMAIN,
                                                'Date': self.created_on,
                                                'primary_physician': self.primary_physician.get_name()
                                                })
                    msg = EmailMessage(subject,
                                       message,
                                       settings.SERVER_EMAIL,
                                       [recipient.email],
                                       headers=Headers,
                                       cc=[primary_recipient.email]
                                       )
                    msg.content_subtype = "html"
                    msg.send()
        if self.status == CASE_STATUS['A']:
            subject = settings.CASE_APPROVED_SUBJECT
        authorized_emails = []
        for entry in recipients:
            authorized_emails.append(str(entry))
        message = render_to_string('email_to_physician.html',
                                   {'id': self.id,
                                    'title': self.title,
                                    'name': primary_recipient.get_name(),
                                    # 'token': token,
                                    'DOMAIN': settings.DOMAIN,
                                    'Date': self. created_on,
                                    'status': self.status,
                                    'history_object': history_obj,
                                    })
        msg = EmailMessage(subject,
                           message,
                           settings.SERVER_EMAIL,
                           [primary_recipient.email],
                           headers=Headers, cc=authorized_emails,
                           bcc=settings.BCC_LIST
                           )
        msg.content_subtype = "html"
        msg.send()

    def ordered_event(self, event_type):
        events = []
        try:
            event = Event.objects.get(casereport=self, previous_event=None,
                                      parent_event=None)
        except:
            return events
        while(event.next_event):
            if event.event_type == event_type and event.is_negation == False:
                events.append(event)
            event = event.next_event
        if event.event_type == event_type and event.is_negation == False:
            events.append(event)
        return events

    def get_treatment_events_in_order(self):
        return self.ordered_event('treatment')

    def get_test_events_in_order(self):
        return self.ordered_event('test')

    def get_diagnosis_events_in_order(self):
        return self.ordered_event('diagnosis')

    def get_physicians_info(self):
        physicians = ''
        for physician in self.referring_physician.all():
            physicians += '%s, ' %physician.name
        else:
            physicians = physicians[:-2]
            physicians += ' - %s' %(physician.affiliation)
        return physicians

    def get_physician(self):
        return self.primary_physician.name

    def get_presented(self):
        event = Event.objects.filter(casereport=self, parent_event__isnull=True)
        return event[0].get_info()

    def get_physician_affiliation(self):
        return self.primary_physician.affiliation

    def get_reported_date(self):
        try:
            event = Event.objects.get(casereport=self, parent_event=None)
        except:
            event = None
        return event.date_point if event else event

    def get_sarcoma_type(self):
        return self.sarcoma_type if not self.sarcoma_type == 'Other' else self.other_sarcoma_type


class Treatment(CRDBBase):
    casereport = models.ForeignKey(CaseReport)
    name = models.CharField(max_length=250)
    treatment_type = models.CharField(max_length=250)
    duration = models.CharField(max_length=250, null=True, blank=True)
    dose = models.CharField(max_length=250, null=True, blank=True)
    objective_response = models.CharField(max_length=2, choices=OBJECTIVE_RESPONSES, null=True, blank=True)
    tumor_size = models.CharField(max_length=50, null=True, blank=True)
    status = models.IntegerField(max_length=1, choices=PERFORMANCE_STATUS, null=True, blank=True)
    treatment_outcome = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class Event(CRDBBase):
    casereport = models.ForeignKey(CaseReport)
    parent_event = models.ForeignKey('self', null=True, blank=True, related_name="parentevent")
    name =  models.CharField(max_length=255)
    frequency = models.IntegerField(null=True, blank=True)
    date_point = models.CharField(max_length=200, null=True, blank=True)  # (year, or actual date)
    end_date_point = models.CharField(max_length=200, null=True, blank=True)  # (year, or actual date)
    interval = models.CharField(max_length=200, null=True, blank=True)  # (e.g. 6 months of therapy)
    previous_event = models.ForeignKey('self', null=True, blank=True, related_name="previousevent")  # use this instead of order
    next_event = models.ForeignKey('self', null=True, blank=True, related_name="nextevent")
    is_negation = models.BooleanField(default=False)
    event_type = models.CharField(max_length=15, choices=TYPE, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_treatment_type(self):
        return self.treatmentevent.treatment_type

    def get_side_effects(self):
        side_effects = self.treatmentevent.side_effects
        return side_effects if side_effects else None

    def get_outcome(self):
        event = self.treatmentevent
        outcome = event.outcome
        while(event.combined_with):
            event = event.combined_with
            outcome = '%s, %s' %(outcome, event.outcome)
        if outcome.strip(', ') == '':
            outcome = ''
        else:
            outcome = outcome.strip(', ')
        return outcome


    def get_name(self):
        event = self.treatmentevent
        name = event.name
        while(event.combined_with):
            name = '%s / %s' %(name, event.combined_with)
            event = event.combined_with
        return name


    def get_combined_with(self):
        return self.treatmentevent.combined_with

    def get_dates(self):
        dates = ''
        if self.date_point:
            dates =  '%s' %self.date_point
        if self.end_date_point:
            dates = '%s' % self.end_date_point
        if (self.date_point and self.end_date_point):
            dates = '%s - %s' %(self.date_point, self.end_date_point)
        return '%s:' %dates if dates else ''

    def get_test_specimen(self):
        specimen = self.testevent.specimen
        return specimen if specimen else 'specimen (Not Specified)'

    def get_body_part(self):
        body_part = self.testevent.body_part
        return body_part if body_part else 'body part (Not Specified)'

    def get_diagnosis_specimen(self):
        specimen = self.diagnosisevent.specimen
        return specimen if specimen else 'specimen (Not Specified)'

    def get_symptoms(self):
        diagnosis = self.diagnosisevent
        symptoms = diagnosis.symptoms
        if diagnosis.body_part:
            symptoms += ' (%s)' %diagnosis.body_part
        return symptoms if symptoms else 'symptoms (Not Specified)'

    def get_test_results(self):
        results = ''
        for result in ResultValueEvent.objects.filter(test=self.testevent):
            value = result.value
            if result.result_indicator:
                value += ' (%s)' %result.result_indicator
            results =  '%s, %s' %(results, value) if results else value
        if not results:
            results = 'results (Not Specified)'
        return results

    def get_info(self):
        if self.date_point:
            return '%s on %s' %(self.name, self.date_point)
        return ''



class TestEvent(Event):
    specimen = models.CharField(max_length=255)
    body_part = models.CharField(max_length=255, null=True, blank=True)

    def save(self):
        self.event_type = 'test'
        super(TestEvent, self).save()

class TreatmentEvent(Event):
    treatment_type = models.CharField(max_length=255)
    followed_by = models.ForeignKey('self', null=True, blank=True)  # - Treatment Event
    followed_by_interval = models.CharField(max_length=50, null=True, blank=True)
    followed_by_interval_unit = models.CharField(max_length=100, null=True, blank=True)
    combined_with = models.ForeignKey('self', null=True, blank=True, related_name="combinedwith")
    side_effects = models.TextField(null=True, blank=True)
    outcome = models.TextField(null=True, blank=True)

    def save(self):
        self.event_type = 'treatment'
        super(TreatmentEvent, self).save()


class ResultValueEvent(CRDBBase):
    test = models.ForeignKey(TestEvent)  # FK (Test Event)
    value = models.CharField(max_length=200)  # 15.6
    result_indicator = models.CharField(max_length=200, null=True,
                                        blank=True)  # high, low, normal (if available or will be null)

    def __unicode__(self):
        return self.value


class DiagnosisEvent(Event):
    test = models.ForeignKey(TestEvent, null=True, blank=True)  # FK (Test Event)
    specimen = models.CharField(max_length=255, null=True, blank=True)
    symptoms = models.TextField(null=True, blank=True)
    body_part = models.CharField(max_length=255, null=True, blank=True)

    def save(self):
        self.event_type = 'diagnosis'
        super(DiagnosisEvent, self).save()


class CaseReportHistory(models.Model):
    case = models.ForeignKey(CaseReport)
    physician = models.TextField(null=True, blank=True)
    molecular_abberations = models.TextField(null=True, blank=True)
    tests = models.TextField(null=True, blank=True)
    treatments = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.case) or ''

    # def __unicode__(self):
    #     return self.case.__unicode__()

