from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.http import JsonResponse
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
            if form.cleaned_data['to_dashboard']:
                members.append(request.user)
            if members:
                shared_content.share_with(members)
            groups = form.cleaned_data['groups']
            if groups:
                shared_content.share_with(groups)
            return JsonResponse({
                'success': True,
                'message': 'Item sent',
            })
        return JsonResponse({
            'success': False,
            'message': 'Sending item failed',
        })
