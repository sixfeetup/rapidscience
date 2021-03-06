from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.generic import View

from casereport.constants import WorkflowState
from casereport.models import CaseReport, action
from rlp.core.email import activity_mail
from rlp.core.forms import get_sendto_form
from rlp.core.utils import resolve_email_targets

MESSAGES_DEFAULT_FORM_ERROR = "Please correct the errors below"


@never_cache
def healthcheck(request):
    """Returns a 2xx response so load balancers can detect whether Django is up and running or not."""
    return HttpResponse("Operational", content_type="text/plain")


@never_cache
def server_error(request, template='500.html'):
    return render(request, template)


def home(request, template='core/home.html'):
    if request.user.is_authenticated():
        return redirect('dashboard')
    return render(request, template)


def about(request, template='core/about.html'):
    return render(request, template)


def privacy_policy(request, template='core/privacy_policy.html'):
    return render(request, template)


def terms_of_use(request, template='core/terms_of_use.html'):
    return render(request, template)


class SendToView(LoginRequiredMixin, View):
    def get(self, request, app_label, model_name, object_id):
        request.session['referrer'] = request.META['HTTP_REFERER']
        ctype = ContentType.objects.get_by_natural_key(app_label, model_name)
        model = ctype.model_class()
        shared_content = get_object_or_404(model, pk=object_id)
        type_key = (app_label, model_name)
        form = get_sendto_form(request.user, shared_content, type_key)
        context = {
            'form': form,
        }
        return render(request, 'core/send_to.html', context)

    def post(self, request, app_label, model_name, object_id):
        ctype = ContentType.objects.get_by_natural_key(app_label, model_name)
        model = ctype.model_class()
        shared_content = get_object_or_404(model, pk=object_id)
        type_key = (app_label, model_name)
        form = get_sendto_form(
            request.user,
            shared_content,
            type_key,
            request.POST,
        )
        if form.is_valid():
            members = list(form.cleaned_data['members'])
            groups = list(form.cleaned_data['groups'])
            last_proj = request.session.get('last_viewed_project')
            if not last_proj:
                # if not coming from a project, remove any self-to-self shares
                if request.user in members:
                    members = [m for m in members if m.id != request.user.id]
            targets = members + groups
            shared_to = shared_content.share_with(
                targets,
                shared_by=request.user,
                comment=form.cleaned_data['comment'],
            )

            if ctype.name != "case report" or \
                (hasattr(shared_content, "workflow_state") and
                 shared_content.workflow_state == WorkflowState.LIVE):
                #    case report emails are handled separately
                targets_as_emails = resolve_email_targets(targets) - shared_to
                activity_mail(request.user, shared_content,
                              targets_as_emails, request)


            # automatically bookmark for user when sharing
            if not shared_content.is_bookmarked_to(request.user):
                # unless this is an admin editing a casereport
                print( shared_content)
                if isinstance(shared_content, CaseReport):
                    is_admin = request.user.is_staff or request.user.is_superuser
                    is_author = request.user.email == shared_content.primary_author.email
                    #      is admin   |   is author
                    #         x       |       x     bookmark it
                    #         o       |       x     bookmark it
                    #         x       |       o     do nothing
                    #         o       |       o     bookmark it
                    print("is admin / is authopr")
                    print(is_admin, is_author)
                    if is_admin and not is_author:
                        pass
                    else:
                        request.user.bookmark(shared_content)
                else:
                    request.user.bookmark(shared_content)

            action.really_send()  # TODO: make this a decorator?
            if 'referrer' in request.session:
                url = request.session['referrer']
                if url:
                    return redirect(url)
        return redirect('/')


class BookmarkView(LoginRequiredMixin, View):
    def post(self, request):
        type_id = request.POST.get('content_type')
        content_type = ContentType.objects.get(id=type_id)
        content_id = request.POST.get('content_id')
        content = content_type.get_object_for_this_type(id=content_id)
        if request.POST.get('dashboard') == 'on':
            request.user.bookmark(content)
        if request.POST.get('group') == 'on':
            initial_proj = request.session.get('last_viewed_project')
            if initial_proj and initial_proj != -1:
                project_type = ContentType.objects.get_by_natural_key(
                    'projects', 'project',
                )
                Project = project_type.model_class()
                group = Project.objects.get(id=initial_proj)
                group.bookmark(content)
        return HttpResponse("Success", content_type="text/plain")


class BookmarkRemoveView(LoginRequiredMixin, View):
    def post(self, request):
        type_id = request.POST.get('content_type')
        content_type = ContentType.objects.get(id=type_id)
        content_id = request.POST.get('content_id')
        content = content_type.get_object_for_this_type(id=content_id)
        if request.POST.get('dashboard') == 'on':
            request.user.remove_bookmark(content)
        if request.POST.get('group') == 'on':
            initial_proj = request.session.get('last_viewed_project')
            if initial_proj and initial_proj != -1:
                project_type = ContentType.objects.get_by_natural_key(
                    'projects', 'project',
                )
                Project = project_type.model_class()
                group = Project.objects.get(id=initial_proj)
                group.remove_bookmark(content)
        return HttpResponse("Success", content_type="text/plain")
