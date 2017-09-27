import json

from actstream import action
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
from django.utils.encoding import force_text
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
try:
    from django.urls import reverse
except ImportError as old_django:
    from django.core.urlresolvers import reverse
from taggit.models import Tag

from casereport import emails
from casereport.api import TreatmentInstanceResource
from casereport.constants import SARCOMA_TYPE, WorkflowState
from casereport.forms import CaseForm
from casereport.forms import MultiFacetedSearchForm
from casereport.havoc_interface import havoc_results
from .models import (
    AuthorizedRep,
    CaseReport,
    SubtypeOption,
    CaseFile,
    Treatment,
    MolecularAbberation
    )

from rlp.accounts.models import User
from rlp.core.forms import member_choices
from rlp.core.forms import group_choices
from rlp.core.utils import bookmark_and_notify, add_tags, fill_tags, \
    resolve_email_targets
from rlp.core.utils import enforce_sharedobject_permissions
from rlp.projects.models import Project
from functools import partial

__author__ = 'yaseen'


def is_review_allowed(user, casereport):
    return (
        user.is_staff or
        user.id == casereport.primary_author.pk
    )


@partial(enforce_sharedobject_permissions, obj_class=CaseReport, id_name='case_id')
class CaseReportDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'casereport/casereport_view.html'

    def get(self, request, case_id, **kwargs):
        casereport = CaseReport.objects.get(id=case_id)
        treatments = Treatment.objects.filter(casereport_f_id=case_id)
        testevents = casereport.event_set.select_related('testevent')
        last_viewed_path = request.session.get('last_viewed_path')
        user_can_comment = casereport.is_shared_with_user(request.user) or request.user == casereport.primary_author
        comment_list = casereport.discussions.all()
        review_allowed = is_review_allowed(self.request.user, casereport)
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

def workflow_transition( request, casereport_id):
    casereport = CaseReport.objects.get(id=casereport_id)

    action = request.GET.get('action')
    msg = casereport.take_action_for_user(action, request.user)
    casereport.save()

    if msg:
        messages.success(request, msg)

    # hack to allow edit actions to use an interstitial form
    if "Edit" in action:
        return HttpResponseRedirect(reverse('edit', kwargs={'case_id':casereport.id}))

    return HttpResponseRedirect(reverse('casereport_detail', kwargs={'case_id':casereport.id, 'title_slug':casereport.title}))

def update_treatments_from_request(case, data):
    """Loop through treatments on the add/edit form,
       create or update treatments as needed
    """
    treatment_pk_list = data.getlist('treatment_pk', None)
    treatment_name_list = data.getlist('treatment_name', None)
    treatment_duration_list = data.getlist('treatment_duration', None)
    treatment_type_list = data.getlist('treatment_type', None)
    treatment_intent_list = data.getlist('treatment_intent', None)
    treatment_response_list = data.getlist('treatment_response', None)
    treatment_status_list = data.getlist('treatment_status', None)
    treatment_outcome_list = data.getlist('treatment_outcome', None)
    for i in range(0, len(treatment_name_list)):
        if not treatment_name_list[i]:
            continue
        if treatment_pk_list[i]:
            # update existing Treatment
            treatment = get_object_or_404(Treatment, pk=treatment_pk_list[i])
            treatment.casereport_f = case
            treatment.name = treatment_name_list[i]
            treatment.duration = treatment_duration_list[i]
            treatment.treatment_type = treatment_type_list[i]
            treatment.treatment_intent = treatment_intent_list[i]
            treatment.objective_response = treatment_response_list[i]
            treatment.status = treatment_status_list[i] or None
            treatment.notes = treatment_outcome_list[i]
            treatment.save()
        else:
            # create new Treatment
            TreatmentInstanceResource()._post(
                case,
                treatment_name_list[i],
                duration=treatment_duration_list[i],
                treatment_type=treatment_type_list[i],
                treatment_intent=treatment_intent_list[i],
                objective_response=treatment_response_list[i],
                status=treatment_status_list[i] or None,
                notes=treatment_outcome_list[i])


class CaseReportFormView(LoginRequiredMixin, FormView):
    template_name = 'casereport/new_add_casereport.html'
    form_class = CaseForm

    def get(self, request, *args, **kwargs):
        heading = 'Submit Case'
        subtypes = SubtypeOption.objects.order_by('name')
        aberrations = MolecularAbberation.objects.all()
        all_members = User.objects.all()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(
            heading=heading,
            form=form,
            subtypes=subtypes,
            aberrations=aberrations,
            all_members=all_members), )

    def get_form(self, form_class):
        try:
            group = Project.objects.get(id=self.request.session.get('last_viewed_project'))
        except Project.DoesNotExist:
            group = []
        form = super(CaseReportFormView, self).get_form(form_class)
        user = self.request.user
        all_members = ((member.id, member.get_full_name()) for member in User.objects.all())
        # form.fields['tags'].queryset = Tag.objects.order_by('slug')
        if group and group.approval_required:
            form.fields['members'].hide_field = True
            form.fields['members'].choices = [(user.id, user.get_full_name())]
            form.fields['members'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['groups'].widget.attrs['class'] = 'select2 hiddenField'
            form.fields['external'].widget.attrs['class'] = 'hiddenField'
            form.fields['comment'].widget.attrs['class'] = 'hiddenField'
        elif group:
            form.fields['members'].choices = all_members
            form.fields['groups'].choices = group_choices(user, exclude=[group])
        else:
            form.fields['members'].choices = all_members
            form.fields['groups'].choices = group_choices(user)
        return form

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        title = data.get('casetitle')
        coauthors = data.getlist('coauthors', None)
        email = data.getlist('coauthor_email')
        name = data.getlist('coauthor_name')
        alt_email = data.get('author', None)
        author_alt = None
        if alt_email:
            author_alt = AuthorizedRep.objects.get_or_create(email=alt_email)
        primary_author = User.objects.get(pk=request.user.id)
        age = data.get('age')
        gender = data.get('gender')
        subtype = None
        if data.get('subtype'):
            subtype = SubtypeOption.objects.get(name=data.get('subtype'))
        subtype_other = data.get('subtype_other')
        attachment1 = request.FILES.get('attachment1')
        attachment2 = request.FILES.get('attachment2')
        attachment3 = request.FILES.get('attachment3')
        attachment1_title = data.get('attachment1_title')
        attachment2_title = data.get('attachment2_title')
        attachment3_title = data.get('attachment3_title')
        attachment1_description = data.get('attachment1_description')
        attachment2_description = data.get('attachment2_description')
        attachment3_description = data.get('attachment3_description')
        document = request.FILES.get('uploadfile')
        presentation = data.get('presentation')
        aberrations = data.getlist('aberrations', None)
        aberrations_other = data.get('aberrations_other')
        biomarkers = data.get('biomarkers')
        pathology = data.get('pathology')
        additional_comment = data.get('additional_comment')
        consent = data.get('consent')
        details = data.get('details')

        case = CaseReport(title=title, age=age, gender=gender,
                          casefile_f=document, subtype=subtype,
                          subtype_other=subtype_other, presentation=presentation,
                          aberrations_other=aberrations_other,
                          biomarkers=biomarkers, pathology=pathology,
                          additional_comment=additional_comment,
                          primary_author=primary_author,
                          free_text=details, consent=consent,
                          attachment1=attachment1,
                          attachment2=attachment2, attachment3=attachment3,
                          attachment1_title=attachment1_title,
                          attachment2_title=attachment2_title,
                          attachment3_title=attachment3_title,
                          attachment1_description=attachment1_description,
                          attachment2_description=attachment2_description,
                          attachment3_description=attachment3_description)
        case.save()
        tags = {}
        tags['ids'] = request.POST.getlist('tags', [])
        tags['new'] = request.POST.getlist('new_tags', [])
        add_tags(case, tags)
        if author_alt:
            case.authorized_reps.add(author_alt[0])
        update_treatments_from_request(case, data)
        if aberrations:
            case.aberrations.add(*aberrations)

        coauthors_to_notify = set()

        for auth in coauthors:
            coauth_user = User.objects.get(pk=auth)
            case.co_author.add(auth)
            coauthors_to_notify.add(coauth_user)
        for i in range(0, len(name)):
            try:
                coauthor = User.objects.get(email=email[i])
                case.co_author.add(coauthor)
                coauthors_to_notify.add(coauthor)
            except User.DoesNotExist:
                coauthor = User(email=email[i], last_name=name[i],
                                is_active=False)
                coauthor.save()
                case.co_author.add(coauthor)

        case.save()
        
        if data.get('sharing-options') == 'share-all':
            cc_group = Project.objects.get(title='Community Commons')
            case.share_with([cc_group], shared_by=case.primary_author)

        bookmark_and_notify(
            case, self, self.request, 'casereport', 'casereport',
            comment=data.get('comment') or None,
        )

        past_tense_verb = 'created'
        for group_id in data.getlist('groups'):
            group = Project.objects.get(id=group_id)
            action.send(
                request.user, verb=past_tense_verb,
                description=data.get('comment'), action_object=case,
                target=group)
        else:
            action.send(
                request.user, verb=past_tense_verb,
                description=data.get('comment'), action_object=case)
        external = data.get('external').split(",")
        for address in external:
            if not address:
                continue
            if not User.objects.filter(email=address):
                new_user = User(email=address, is_active=False)
                new_user.save()
                case.share_with(
                    [new_user], shared_by=primary_author,
                    comment=data.get('comment'))


        # eventually we' want this:
        # #messages.success(self.request, "Saved!")
        # return redirect(reverse('casereport_detail', args=(case.id, case.title)))
        if case.workflow_state == WorkflowState.DRAFT:
            messages.success(self.request, "Your case report has been " +
                             "successfully saved. To send to the editorial" +
                             " team, please click the “submit” button below.")
            return redirect(case.get_absolute_url())
        else:
            self.template_name = 'casereport/add_casereport_success.html'
            self.case_success_mail(primary_author, coauthors, author_alt)
            return self.render_to_response({'case_number': case.id})

    def case_success_mail(self, author, coauthors, author_alt):
        Headers = {'Reply-To': settings.CRDB_SERVER_EMAIL}
        recipient = author
        copied = []
        copied.append(author_alt)
        copied = copied + [i.email for i in coauthors] + [settings.DEFAULT_FROM_EMAIL]
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
        subtypes = SubtypeOption.objects.order_by('name')
        aberrations = MolecularAbberation.objects.all()
        if ftype == 'F':
            self.template_name = 'casereport/fileform.html'
        elif ftype == "T":

            self.template_name = 'casereport/free-text.html'
            return self.render_to_response(dict(subtypes=subtypes))
        return self.render_to_response(dict(subtypes=subtypes, aberrations=aberrations))


def limit_casereport_results(queryset, user):
    """Limit the case results in a queryset so
       users only see what they are supposed to see.
       Admins should see all results. Any other users
       only see what they created or is shared with them.
    """
    # admins see all results
    if user.is_staff:
        return queryset

    # non-admins only see their own cases
    # or cases shared with them
    # or cases shared with group to which the user belongs
    shared_pks = set()
    for item in user.get_shared_content(CaseReport):
        if item.workflow_state == WorkflowState.LIVE:
            shared_pks.update([item.pk, ])
    for group in user.active_projects():
        for item in group.get_shared_content(CaseReport):
            if item.workflow_state == WorkflowState.LIVE:
                shared_pks.update([item.pk, ])
    user = User.objects.get(email=user.email)
    authored_pks = set({cr.pk for cr in CaseReport.objects.filter(primary_author=user)})
    shared_pks.update(authored_pks)

    for result in queryset:
        if result.content_type() != 'casereport.casereport':
            continue
        if int(result.pk) not in shared_pks:
            queryset = queryset.exclude(id=result.id)
    return queryset


class MyFacetedSearchView(FacetedSearchView):
    def __init__(self, *args, **kwargs):
        sqs = SearchQuerySet().using('casescentral').models(CaseReport).highlight(fragsize=200)
        kwargs.update({'form_class': MultiFacetedSearchForm, 'searchqueryset': sqs})
        super(MyFacetedSearchView, self).__init__(*args, **kwargs)

    def __call__(self, request):
        if request.is_ajax():
            self.template = 'casereport/search/results.html'
        else:
            self.template = 'casereport/search/search.html'
        # if Cases Central was viewed, prevent adding things to a group
        request.session['last_viewed_project'] = None
        return super(MyFacetedSearchView, self).__call__(request)

    def get_results(self):
        """
        Fetches the results via the form.

        Returns an empty list if there's no query to search with.
        """
        sqs = self.form.searchqueryset
        sqs = sqs.facet(u'{!ex=GENDER}gender_exact', sort="index")
        sqs = sqs.facet(u'{!ex=COUNTRY}country_exact', sort="index")
        sqs = sqs.facet(u'treatment_type')
        self.form.searchqueryset = sqs
        results = self.form.search()
        if not results:
            return results

        results = limit_casereport_results(results, self.request.user)
        return results.order_by('-pub_or_mod_date')

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
        # keep genders sorted
        context['facets']['fields']['gender'] = sorted(
            context['facets']['fields']['gender'],
            key=lambda g: g[0],
        )
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
        heading = 'Edit Case'
        casereport = get_object_or_404(CaseReport, id=case_id)
        subtypes = SubtypeOption.objects.order_by('name')
        aberrations = MolecularAbberation.objects.all()
        all_members = User.objects.all()
        form = self.form_class()
        form.fields['members'].choices = member_choices()
        form.fields['groups'].choices = group_choices(request.user)
        # show who the case is already shared with
        shared_with = casereport.get_viewers()
        form.fields['members'].initial = []
        form.fields['groups'].initial = []
        cr_shared = 'none'
        for viewer in shared_with:
            if viewer._meta.model_name == 'user':
                form.fields['members'].initial.append(viewer.id)
                cr_shared = 'pick'
            elif viewer._meta.model_name == 'project':
                form.fields['groups'].initial.append(viewer.id)
                cr_shared = (viewer.id == 1) and 'all' or 'pick'
        fill_tags(casereport, form)

        return self.render_to_response(self.get_context_data(
            heading=heading,
            form=form,
            casereport=casereport,
            subtypes=subtypes,
            aberrations=aberrations,
            all_members=all_members,
            cr_shared=cr_shared), )

    def post(self, request, case_id, *args, **kwargs):
        data = request.POST.copy()
        case = get_object_or_404(CaseReport, id=case_id)
        case.title = data['casetitle']
        alt_email = data.get('author', None)
        subtype = data.get('subtype', None)
        case.authorized_reps.clear()
        if alt_email:
            author = AuthorizedRep.objects.get_or_create(email=alt_email)
            if author:
                case.authorized_reps.add(author[0])

        # co-authors
        current_authors = set(case.co_author.all())
        case.co_author = data.getlist('coauthors')
        email = data.getlist('coauthor_email')
        name = data.getlist('coauthor_name')

        # find new coauthors that need to be notified or invited
        new_coauthors = set()
        for auth in data.getlist('coauthors'):
            coauth_user = User.objects.get(pk=auth)
            if coauth_user not in current_authors:
                new_coauthors.add(coauth_user)
        for i in range(0, len(email)):
            try:
                coauthor = User.objects.get(email=email[i])
                if coauthor not in current_authors:
                    new_coauthors.add(coauthor)
                    case.co_author.add(coauthor)
            except User.DoesNotExist:
                coauthor = User(email=email[i], last_name=name[i],
                                is_active=False)
                coauthor.save()
                case.co_author.add(coauthor)
                if case.workflow_state != WorkflowState.DRAFT:
                    emails.invite_coauthor(case, coauthor)

        for recipient in new_coauthors:
            if case.workflow_state != WorkflowState.DRAFT:
                emails.notify_coauthor(case, recipient)

        case.age = data['age']
        case.gender = data['gender']
        if subtype:
            case.subtype = SubtypeOption.objects.get(name=data['subtype'])
        case.subtype_other = data['subtype_other']
        case.presentation = data['presentation']
        case.aberrations.clear()
        if data.getlist('aberrations', None):
            case.aberrations.add(*data.getlist('aberrations', None))
        case.aberrations_other = data['aberrations_other']
        case.biomarkers = data['biomarkers']
        case.pathology = data['pathology']
        update_treatments_from_request(case, data)
        case.free_text = data['details']
        case.additional_comment = data['additional_comment']
        case.consent = data['consent']
        # attachments & files
        if 'attachment1_title' in data:
            case.attachment1 = request.FILES.get('attachment1') or case.attachment1
            case.attachment1_title = data['attachment1_title']
            case.attachment1_description = data['attachment1_description']
        if 'attachment2_title' in data:
            case.attachment2 = request.FILES.get('attachment2') or case.attachment2
            case.attachment2_title = data['attachment2_title']
            case.attachment2_description = data['attachment2_description']
        if 'attachment3_title' in data:
            case.attachment3 = request.FILES.get('attachment3') or case.attachment3
            case.attachment3_title = data['attachment3_title']
            case.attachment3_description = data['attachment3_description']
        if 'uploadfile' in request.FILES:
            case.casefile_f = request.FILES.get('uploadfile') or case.casefile_f

        # any edit by an admin needs to clear the author approved.
        if request.user.is_staff and request.user.email != case.primary_author.email:
            case.author_approved = False
        tags = {}
        tags['ids'] = request.POST.getlist('tags', [])
        tags['new'] = request.POST.getlist('new_tags', [])
        add_tags(case, tags)

        case.save()
        bookmark_and_notify(
            case, self, self.request, 'casereport', 'casereport',
        )

        past_tense_verb = 'updated'
        for group in data.getlist('groups'):
            print( request.user, past_tense_verb, case, group )

        if data.get('sharing-options') == 'share-all':
            cc_group = Project.objects.get(title='Community Commons')
            case.share_with([cc_group], shared_by=case.primary_author)

        external = data.get('external').split(",")
        for address in external:
            if not address:
                continue
            if not User.objects.filter(email=address):
                new_user = User(email=address, is_active=False)
                new_user.save()
                case.share_with([new_user], shared_by=case.primary_author)

        messages.success(request, "Edits saved!")
        return redirect(reverse('casereport_detail', args=(case.id, case.title)))


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
