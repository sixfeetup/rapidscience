import json
from ajax_select import registry
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.core import management
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from casereport.constants import COUNTRIES
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic import TemplateView

from casereport.api import AbberationListResource
from casereport.api import AuthorizedListResource
from casereport.api import InstitutionInstanceResource
from casereport.api import PhysicianInstanceResource
from casereport.api import CaseReportInstanceResource
from casereport.api import CaseReportListResource
from casereport.api import CaseReportHistoryInstanceResource
from casereport.api import TreatmentInstanceResource
from casereport.constants import GENDER
from casereport.constants import SARCOMA_TYPE
from casereport.decorator import validate_token
from casereport.forms import CaptchaForm
from casereport.forms import FacetedSearchForm
from casereport.havoc_interface import havoc_results
from casereport.models import CaseReport
from casereport.models import CaseFile
from casereport.models import Treatment
from django.core.mail import EmailMessage

__author__ = 'yaseen'


class CaseReportDetailView(TemplateView):
    template_name = 'casereport/search_results.html'

    def get(self, request, case_id, **kwargs):
        casereport = CaseReport.objects.get(id=case_id)
        treatments = Treatment.objects.filter(casereport_f_id=case_id)
        testevents = casereport.event_set.select_related('testevent')
        if casereport.casefile_f:
            return self.render_to_response(dict(casereport=casereport,
                                                test=testevents,
                                                casefile=casereport.casefile_f))

        return self.render_to_response(dict(casereport=casereport, test=testevents,treatments=treatments))

class CaseReportFormView(FormView):
    template_name = 'casereport/new_add_casereport.html'
    form_class = CaptchaForm
    def get(self, request, *args, **kwargs):
        captchaform = self.form_class()
        data = request.GET.copy()
        cap_only = data.get('caponly', None)
        if request.is_ajax():
            if 'casereport' in request.META['HTTP_REFERER'] or cap_only:
                newcap = self.get_new_captcha()
                return HttpResponse(json.dumps(newcap), content_type='application/json')
            return self.render_to_response(dict(captchaform=captchaform, countries=COUNTRIES))

        return self.render_to_response(dict(captchaform=captchaform, countries=COUNTRIES))

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        if request.is_ajax():
            captcha_data = dict(captcha_0=data.get('captcha_0'),
                                captcha_1=data.get('captcha_1'),
                                csrftoken=data.get("csrfmiddlewaretoken"))
            is_captcha_valid = self.validate_captcha(captcha_data)
            if not is_captcha_valid:
                newcap = self.get_new_captcha()
                return HttpResponse(json.dumps(newcap), content_type='application/json')
            return HttpResponse('OK')
        entry_type = data.get('entry-type')
        refering_doctor = data.getlist('physician', None)
        email = data.getlist('email')
        institution = data.get('institution')
        city = data.get('city')
        country = data.get('physician_country')
        author = data.getlist('author', None)
        author_list = AuthorizedListResource()._post(email=author)
        institution = InstitutionInstanceResource()._post(institution, city, country)
        physicians = []
        for i in range(0, len(refering_doctor)):
            physician = PhysicianInstanceResource()._post(refering_doctor[i],
                email[i], institution)
            physicians.append(physician)
        if entry_type == 'F':
            document = request.FILES['file']
            file_name = request.FILES['file'].name
            case = CaseReportListResource()._post(physicians=physicians,
                document=document, file_name=file_name)
            CaseReportInstanceResource()._addauthor(case, author_list)
        elif entry_type == 'M':
            title = data.get('title')
            age = data.get('age')
            gender = data.get('gender')
            index = data.get('index')
            pathology = data.get('pathology')
            progression = data.get('progression')
            response = data.get('response')
            treatment_name = data.getlist('treatment_name', None)
            dose = data.getlist('dose', None)
            duration = data.getlist('treatment_length', None)
            status = data.getlist('status', None)
            objective_response = data.getlist('objective_response', None)
            tumor_size = data.getlist('tumor_size', None)
            notes = data.getlist('notes', None)
            treatment_outcome = data.getlist('treatment_outcome', None)
            additional_comment = data.get('additional_comment')
            test = data.getlist('test', None)
            test_result = data.getlist('test_result', None)
            sarcoma = data.get('sarcoma')
            other_sarcoma = data.get('other-sarcoma')
            m_abbs = AbberationListResource()._post(molecule=test, abberation=test_result)
            case = CaseReportListResource()._post(title=title, age=age,
                                gender=gender, pathology=pathology,
                                progression=progression,
                                response=response,
                                additional_comment=additional_comment,
                                index=index, physicians=physicians,sarcoma_type=sarcoma, other_sarcoma=other_sarcoma)
            for i in range(0, len(treatment_name)):
                if treatment_name[i]:
                    treatment_type = data.getlist('treatment_type_%s' %i, None)
                    duration = data.get('treatment_length_%s' %i, None)
                    dose = data.get('dose_%s' %i, None)
                    objective_response = data.get('objective_response_%s' %i, None)
                    status = data.get('status_%s' %i, None)
                    tumor_size = data.get('tumor_size_%s' %i, None)
                    treatment_outcome = data.get('treatment_outcome_%s' %i, None)
                    notes = data.get('notes_%s' %i, None)
                    TreatmentInstanceResource()._post(case, treatment_name[i], ','.join(treatment_type), duration=duration, dose=dose,
                        objective_response = objective_response, tumor_size=tumor_size,
                        status=status, treatment_outcome=treatment_outcome,notes=notes)
            CaseReportInstanceResource()._addauthor(case, author_list)

            CaseReportInstanceResource()._addabberations(case, m_abbs)

        elif entry_type == 'T':
            age = data.get('age-field')
            gender = data.get('gender-field')
            sarcoma = data.get('sarcoma')
            other_sarcoma = data.get('other-sarcoma')
            details = data.get('details')
            case = CaseReportListResource()._post(physicians=physicians,age=age,gender=gender, sarcoma_type=sarcoma, other_sarcoma=other_sarcoma, details=details)
            CaseReportInstanceResource()._addauthor(case, author_list)

        self.template_name = 'casereport/add_casereport_success.html'
        self.case_success_mail(physicians, author_list)
        return self.render_to_response({})

    def case_success_mail(self, physicians, author_list):
        Headers = {'Reply-To': settings.CRDB_SERVER_EMAIL}
        recipient = physicians[0]
        authorized_recipient = []
        for i in author_list:
            authorized_recipient.append(str(i))
        message = render_to_string('casereport/case_submit_email.html', {'name': recipient.get_name(),
                                                              'DOMAIN': settings.CRDB_DOMAIN})
        msg = EmailMessage(settings.CASE_SUBMIT, message, settings.CRDB_SERVER_EMAIL, [recipient.email],
                           headers=Headers, cc=authorized_recipient, bcc=settings.CRDB_BCC_LIST)
        msg.content_subtype = "html"
        msg.send()

    def validate_captcha(self, data):
        form = self.form_class(data)
        if form.is_valid():
            return True
        return False

    def get_new_captcha(self):
        newcap = dict()
        newcap['status'] = 0
        newcap['new_cptch_key'] = CaptchaStore.generate_key()
        newcap['new_cptch_image'] = captcha_image_url(newcap['new_cptch_key'])
        return newcap


class AutoCompleteView(FormView):
    def get(self, request, *args, **kwargs):
        data = request.GET
        q = data.get("term")
        results = havoc_results(api='concepts', vocab='hgnc', term=q+'%', partial=True)
        results = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(results, mimetype)


class FormTypeView(TemplateView):
    template_name = 'casereport/manualform.html'

    def get(self, request, **kwargs):
        ftype = request.GET.get('ftype', '')
        sarcoma = sorted(SARCOMA_TYPE)
        if ftype == 'F':
            self.template_name = 'casereport/fileform.html'
        elif ftype == "T":

            self.template_name = 'casereport/free-text.html'
            return self.render_to_response(dict(sarcoma=sarcoma))
        return self.render_to_response(dict(sarcoma=sarcoma))


class MyFacetedSearchView(FacetedSearchView):
    def __init__(self, *args, **kwargs):
        sqs = SearchQuerySet().facet('gender', sort='index')\
            .facet('age', sort='index')\
            .facet('molecular_abberations', sort='count')\
            .facet('country', sort='count')\
            .facet('molecules', sort='count')\
            .facet('treatments', sort='count')\
            .facet('cr_tests', sort='count')\
            .facet('treatment_type', sort='count')\
            .highlight(fragsize=200)
        kwargs.update({'form_class': FacetedSearchForm, 'searchqueryset': sqs})
        super(MyFacetedSearchView, self).__init__(*args, **kwargs)

    def __call__(self, request):
        if request.is_ajax():
            self.template = 'casereport/search/results.html'
        else:
            self.template = 'casereport/search/search.html'
        return super(MyFacetedSearchView, self).__call__(request)

    def get_results(self):
        """
        Fetches the results via the form.

        Returns an empty list if there's no query to search with.
        """
        data = self.request.GET.copy()
        results = self.form.search()
        if not results:
            return results
        sortby = data.get('sortby')
        if sortby=="created_on":
            sortorder = data.get('sortorder', 'desc')
            if sortorder == 'desc':
                results = results.order_by('-'+sortby)
                return results
            results = results.order_by(sortby)
        else:
            return results
        return results

    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()
        data = self.request.GET.copy()
        sortby = data.get('sortby', 'relevance')
        sortorder = data.get('sortorder', 'desc')
        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
            'sortby': sortby,
            'sortorder': sortorder,
        }

        if not self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            try:
                context['suggestions'] = self.form.get_suggestion()[1]['suggestion']
            except:
                context['suggestions'] = []

        context.update(self.extra_context())
        form_class = CaptchaForm
        captchaform = form_class()
        data = self.request.GET.copy()
        cap_only = data.get('caponly', None)
        if self.request.is_ajax():
            if 'casereport' in self.request.META['HTTP_REFERER'] or cap_only:
                newcap = CaseReportFormView().get_new_captcha()
                return HttpResponse(json.dumps(newcap), content_type='application/json')
            return render_to_response(dict(captchaform=captchaform, countries=COUNTRIES))

        context['captchaform'] = captchaform
        context['countries'] = COUNTRIES
        return render_to_response(
            self.template, context,
            context_instance=RequestContext(self.request),
        )



def ajax_lookup(request, channel):
    if request.method == "GET":
        if 'term' not in request.GET:
            return HttpResponse('')
        query = request.GET['term']
    else:
        if 'term' not in request.POST:
            return HttpResponse('')  # suspicious
        query = request.POST['term']

    lookup = registry.get(channel)
    if hasattr(lookup, 'check_auth'):
        lookup.check_auth(request)

    if len(query) >= getattr(lookup, 'min_length', 1):
        instances = lookup.get_query(query, request)
    else:
        instances = []

    results = json.dumps([
        {
            'pk': force_text(lookup.get_value(item)),
            'value': lookup.get_result(item),
            'match': lookup.format_match(item),
            'repr': lookup.format_item_display(item)
        } for item in instances
    ])

    return HttpResponse(results, content_type='application/json')


def reindexsolr(request):
    management.call_command('rebuild_index', interactive=False)
    return HttpResponse('Indexing Complete')


def downloadfile(request, file_id):
    casefile = CaseFile.objects.get(id=file_id)
    source = casefile.document
    response = HttpResponse(source, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' %casefile.document
    return response


class CaseReportEditView(TemplateView):
    template_name = 'casereport/case_edit.html'

    @method_decorator(validate_token)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CaseReportEditView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        case_id = kwargs.get('case_id')
        casereport = get_object_or_404(CaseReport, id=case_id)
        treatments = Treatment.objects.filter(casereport_id=case_id)
        testevents = casereport.event_set.select_related('testevent')
        kwargs = {'casereport': casereport, 'gender': GENDER, 'sarcoma_types': SARCOMA_TYPE,
                  'casefile': casereport.casefile_f, 'treatments': treatments, 'test': testevents}
        return self.render_to_response(kwargs)

    def post(self, *args, **kwargs):
        case_id = kwargs.get('case_id')
        case = get_object_or_404(CaseReport, id=case_id)
        data = self.request.POST
        action = data.get('action', None)
        if action == 'Approve':
            CaseReportInstanceResource().approve(case_id=case_id)
            context = {'message': settings.APPROVED_MESSAGE, 'back_link_label': None, 'back_link': None }

        else:
            title = data.get('title', None)
            age = data.get('age', None)
            gender = data.get('gender', None)
            sarcoma_type = data.get('sarcoma_type', None)
            physician = data.get('physician', None)
            tests = data.get('tests', None)
            treatments = data.get('treatments', None)
            diagnosis = data.get('diagnosis', None)
            molecular_abberations = data.get('molecular_abberations', None)
            CaseReportInstanceResource().update(case_id=case_id, title=title,
                age=age, gender=gender, sarcoma_type=sarcoma_type)
            CaseReportHistoryInstanceResource().post(case=case, physician=physician,
                            tests=tests, treatments=treatments, diagnosis=diagnosis,
                            molecular_abberations=molecular_abberations)
            context = {'message': settings.EDITED_MESSAGE, 'back_link_label': None, 'back_link': None }
        message = render_to_string('casereport/message.html', context)
        return HttpResponse(json.dumps({'message': message}), content_type='application/json')





