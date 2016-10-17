from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache


MESSAGES_DEFAULT_FORM_ERROR = "Please correct the errors below"


@never_cache
def healthcheck(request):
    """Returns a 2xx response so load balancers can detect whether Django is up and running or not."""
    return HttpResponse("Operational", content_type="text/plain")


@never_cache
def server_error(request, template='500.html'):
    return render(request, template)

