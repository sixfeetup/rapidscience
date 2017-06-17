from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.generic import View

from rlp.core.forms import get_sendto_form


MESSAGES_DEFAULT_FORM_ERROR = "Please correct the errors below"


@never_cache
def healthcheck(request):
    """Returns a 2xx response so load balancers can detect whether Django is up and running or not."""
    return HttpResponse("Operational", content_type="text/plain")


@never_cache
def server_error(request, template='500.html'):
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
            if form.cleaned_data['to_dashboard']:
                members.append(request.user)
                request.user.bookmark(shared_content)
            shared_content.share_with(
                members + groups,
                shared_by=request.user,
                comment=form.cleaned_data['comment'],
            )
            # automatically bookmark for user when sharing
            if not shared_content.is_bookmarked_to(request.user):
                request.user.bookmark(shared_content)
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
            if initial_proj:
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
            if initial_proj:
                project_type = ContentType.objects.get_by_natural_key(
                    'projects', 'project',
                )
                Project = project_type.model_class()
                group = Project.objects.get(id=initial_proj)
                group.remove_bookmark(content)
        return HttpResponse("Success", content_type="text/plain")
