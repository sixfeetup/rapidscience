import json
from ajax_select import registry
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, redirect
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
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

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
from casereport.forms import CaseForm
from casereport.forms import MultiFacetedSearchForm
from casereport.havoc_interface import havoc_results
from .models import (
    CaseReport,
    CaseReportReview,
    CaseFile,
    Treatment,
    MolecularAbberation,
    Physician
    )

from rlp.accounts.models import User
from rlp.core.forms import group_choices
from rlp.core.views import SendToView
from rlp.core.utils import enforce_sharedobject_permissions
from rlp.projects.models import Project
from functools import partial

__author__ = 'yaseen'


def is_review_allowed(user, casereport):
    return (
        user.is_superuser or
        user.id == casereport.primary_physician.get_rlpuser()
    )


@partial(enforce_sharedobject_permissions, obj_class=CaseReport, id_name='case_id')
class CaseReportDetailView(TemplateView):
    template_name = 'casereport/casereport_view.html'

    def get(self, request, case_id, **kwargs):
        casereport = CaseReport.objects.get(id=case_id)
        treatments = Treatment.objects.filter(casereport_f_id=case_id)
        testevents = casereport.event_set.select_related('testevent')
        last_viewed_path = request.session.get('last_viewed_path')
        user_can_comment = casereport.is_shared_with_user(request.user)
        comment_list = casereport.discussions.all()
        review_allowed = is_review_allowed(self.request.user, casereport)
        if casereport.casefile_f:
            return self.render_to_response(
                dict(
                    casereport=casereport,
                    test=testevents,
                    casefile=casereport.casefile_f,
                    comment_list=comment_list,
                    user_interaction=user_can_comment,
                    review_allowed=review_allowed,
                    last_viewed_path=last_viewed_path,
                )
            )

        return self.render_to_response(
            dict(
                casereport=casereport,
                test=testevents,
                treatments=treatments,
                comment_list=comment_list,
                user_interaction=user_can_comment,
                review_allowed=review_allowed,
                last_viewed_path=last_viewed_path,
            )
        )


class CaseReportFormView(LoginRequiredMixin, FormView):
    template_name = 'casereport/new_add_casereport.html'
    form_class = CaseForm

    def get(self, request, *args, **kwargs):
        sarcoma = sorted(SARCOMA_TYPE)
        aberrations = MolecularAbberation.objects.all()
        form = self.form_class()
        return self.render_to_response(self.get_context_data(
            form=form,
            sarcoma=sarcoma,
            aberrations=aberrations), )

    def get_form(self, form_class):
        came_from = self.request.GET.get('id')
        try:
            group = Project.objects.get(id=self.request.GET.get('id'))
        except Project.DoesNotExist:
            group = []
        form = super(CaseReportFormView, self).get_form(form_class)
        user = self.request.user
        all_members = ((member.id, member.get_full_name()) for member in User.objects.all())
        if group and group.approval_required:
            form.fields['members'].hide_field = True
            form.fields['members'].choices = [(user.id, user.get_full_name())]
            form.fields['members'].initial = [user.id]
            form.fields['groups'].choices = [(group.id, group.title)]
            form.fields['groups'].initial = [group.id]
            form.fields['members'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['groups'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['external'].widget.attrs['class'] = 'hiddenField'
            form.fields['invitation_message'].widget.attrs['class'] = 'hiddenField'
        else:
            form.fields['members'].choices = all_members
            form.fields['members'].initial = [user.id]
            form.fields['groups'].choices = group_choices(user)
            form.fields['groups'].initial = [came_from]
        return form

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        entry_type = data.get('entry-type')
        title = data.get('casetitle')
        email = data.getlist('physician_email')
        name = data.getlist('physician_name')
        author = data.get('author', None)
        author_list = AuthorizedListResource()._post(email=author)
        physicians = []
        primary_physician = PhysicianInstanceResource()._post(request.user.get_full_name(), request.user.email)
        physicians.append(primary_physician)
        for i in range(0, len(name)):
            physician = PhysicianInstanceResource()._post(name[i], email[i])
            physicians.append(physician)
        age = data.get('age')
        gender = data.get('gender')
        subtype = data.get('subtype')
        attachment1 = request.FILES.get('attachment1')
        attachment2 = request.FILES.get('attachment2')
        attachment3 = request.FILES.get('attachment3')
        attachment1_title = data.get('attachment1_title')
        attachment2_title = data.get('attachment2_title')
        attachment3_title = data.get('attachment3_title')
        attachment1_description = data.get('attachment1_description')
        attachment2_description = data.get('attachment2_description')
        attachment3_description = data.get('attachment3_description')
        if entry_type == 'F':
            document = request.FILES['uploadfile']
            file_name = request.FILES['uploadfile'].name
            case = CaseReportListResource()._post(
                title=title, physicians=physicians, age=age,
                gender=gender, subtype=subtype,
                document=document, file_name=file_name,
                attachment1=attachment1, attachment2=attachment2, attachment3=attachment3,
                attachment1_title=attachment1_title, attachment2_title=attachment2_title,
                attachment3_title=attachment3_title,
                attachment1_description=attachment1_description, attachment2_description=attachment2_description,
                attachment3_description=attachment3_description)
            CaseReportInstanceResource()._addauthor(case, author_list)
        elif entry_type == 'M':
            presentation = data.get('presentation')
            aberrations = data.getlist('aberrations', None)
            aberrations_other = data.get('aberrations_other')
            biomarkers = data.get('biomarkers')
            pathology = data.get('pathology')
            treatment_name_list = data.getlist('treatment_name', None)
            treatment_duration_list = data.getlist('treatment_duration', None)
            treatment_type_list = data.getlist('treatment_type', None)
            treatment_intent_list = data.getlist('treatment_intent', None)
            treatment_response_list = data.getlist('treatment_response', None)
            treatment_status_list = data.getlist('treatment_status', None)
            treatment_outcome_list = data.getlist('treatment_outcome', None)
            additional_comment = data.get('additional_comment')
            case = CaseReportListResource()._post(
                title=title, age=age,
                gender=gender, pathology=pathology,
                additional_comment=additional_comment,
                physicians=physicians, subtype=subtype,
                presentation=presentation, aberrations=aberrations, aberrations_other=aberrations_other,
                biomarkers=biomarkers,
                attachment1=attachment1, attachment2=attachment2, attachment3=attachment3,
                attachment1_title=attachment1_title, attachment2_title=attachment2_title,
                attachment3_title=attachment3_title,
                attachment1_description=attachment1_description, attachment2_description=attachment2_description,
                attachment3_description=attachment3_description)
            for i in range(0, len(treatment_name_list)):
                if treatment_name_list[i]:
                    treatment_name = treatment_name_list[i]
                    duration = treatment_duration_list[i]
                    treatment_type = treatment_type_list[i]
                    treatment_intent = treatment_intent_list[i]
                    treatment_response = treatment_response_list[i]
                    treatment_status = treatment_status_list[i]
                    treatment_outcome = treatment_outcome_list[i]
                    TreatmentInstanceResource()._post(
                        case, treatment_name,
                        duration=duration,
                        treatment_type=treatment_type,
                        treatment_intent=treatment_intent,
                        objective_response=treatment_response,
                        status=treatment_status,
                        notes=treatment_outcome)
            CaseReportInstanceResource()._addauthor(case, author_list)

        elif entry_type == 'T':
            details = data.get('details')
            case = CaseReportListResource()._post(
                title=title, physicians=physicians, age=age, gender=gender,
                subtype=subtype, details=details,
                attachment1=attachment1, attachment2=attachment2, attachment3=attachment3,
                attachment1_title=attachment1_title, attachment2_title=attachment2_title,
                attachment3_title=attachment3_title,
                attachment1_description=attachment1_description, attachment2_description=attachment2_description,
                attachment3_description=attachment3_description)
            CaseReportInstanceResource()._addauthor(case, author_list)

        SendToView.post(
            self, self.request, 'casereport',
            'casereport', case.id,
        )
        if case.status == 'draft':
            messages.success(self.request, "Saved!")
            return redirect(case.get_absolute_url())
        else:
            self.template_name = 'casereport/add_casereport_success.html'
            self.case_success_mail(physicians, author)
            return self.render_to_response({'case_number': case.id})

    def case_success_mail(self, physicians, author):
        Headers = {'Reply-To': settings.CRDB_SERVER_EMAIL}
        recipient = physicians[0]
        copied = []
        copied.append(author)
        coauthors = physicians[1:]
        copied = copied + [i.email for i in coauthors] + ['support@rapidscience.org ']
        message = render_to_string('casereport/case_submit_email.html', {'name': recipient.get_name(),
                                                              'DOMAIN': settings.CRDB_DOMAIN})
        msg = EmailMessage(settings.CASE_SUBMIT, message, settings.CRDB_SERVER_EMAIL, [recipient.email],
                           headers=Headers, cc=copied, bcc=settings.CRDB_BCC_LIST)
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
        aberrations = MolecularAbberation.objects.all()
        if ftype == 'F':
            self.template_name = 'casereport/fileform.html'
        elif ftype == "T":

            self.template_name = 'casereport/free-text.html'
            return self.render_to_response(dict(sarcoma=sarcoma))
        return self.render_to_response(dict(sarcoma=sarcoma, aberrations=aberrations))


class MyFacetedSearchView(FacetedSearchView):
    def __init__(self, *args, **kwargs):
        sqs = SearchQuerySet().models(CaseReport).highlight(fragsize=200)
        kwargs.update({'form_class': MultiFacetedSearchForm, 'searchqueryset': sqs})
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
        sqs = self.form.searchqueryset
        sqs = sqs.facet(u'{!ex=GENDER}gender_exact', sort="index")
        sqs = sqs.facet(u'{!ex=COUNTRY}country_exact', sort="index")
        sqs = sqs.facet(u'treatment_type')
        self.form.searchqueryset = sqs
        results = self.form.search()
        if not results:
            return results

        # get Case Reports that user created or shared to
        shared_pks = [x.pk for x in self.request.user.get_shared_content(CaseReport)]
        try:
            phys = Physician.objects.filter(email=self.request.user.email)
            authored = []
            for phy in phys:
                authored += CaseReport.objects.filter(primary_physician=phy)
            authored_pks = [x.pk for x in authored]
            shared_pks = set(shared_pks + authored_pks)
        except Physician.DoesNotExist:
            pass
        for case in results:
            if case.pk not in shared_pks:
                results = results.exclude(id=case.id)
        sortby = data.get('sortby')
        if sortby == "created_on":
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
        if self.request.session.get('last_viewed_path',None):
            del(self.request.session['last_viewed_path'])
        else:
            print("casereport.views.create_response tried to delete last_viewed_path that did not exist.")
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
        form_class = CaseForm
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


def downloadfile(request, file_id):
    casefile = CaseFile.objects.get(id=file_id)
    source = casefile.document
    response = HttpResponse(source, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' %casefile.document
    return response


class CaseReportEditView(LoginRequiredMixin, FormView):
    form_class = CaseForm
    template_name = 'casereport/new_add_casereport.html'

    def get(self, request, case_id):
        casereport = get_object_or_404(CaseReport, id=case_id)
        sarcoma = sorted(SARCOMA_TYPE)
        aberrations = MolecularAbberation.objects.all()
        form = self.form_class()
        return self.render_to_response(self.get_context_data(
            form=form,
            casereport=casereport,
            sarcoma=sarcoma,
            aberrations=aberrations), )

    def post(self, request, case_id, *args, **kwargs):
        data = request.POST.copy()
        messages.info(request, "Edits saved!")
        case = get_object_or_404(CaseReport, id=case_id)
        case.title = data['casetitle']
        case.save()
        SendToView.post(
            self, self.request, 'casereport',
            'casereport', case.id,
        )
        if case.status == 'draft':
            messages.success(self.request, "Saved!")
            return redirect(case.get_absolute_url())
        else:
            self.template_name = 'casereport/add_casereport_success.html'
            # self.case_success_mail(physicians, author)
            return self.render_to_response({'case_number': case.id})


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = CaseReport
    template_name = 'casereport/review_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ReviewDetailView, self).get_context_data(**kwargs)
        case = context.get('casereport')
        if case is None:
            return
        if case.review:
            context['review'] = case.review
            context['review_allowed'] = is_review_allowed(
                self.request.user,
                case,
            )
            context['comment_list'] = case.review.discussions
        return context
