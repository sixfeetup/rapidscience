from django.conf.urls import patterns, url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from functools import wraps

from .views import AutoCompleteView
from .views import CaseReportDetailView
from .views import CaseReportEditView
from .views import CaseReportFormView
from .views import downloadfile
from .views import FormTypeView
from .views import MyFacetedSearchView
from .views import ReviewDetailView
from .views import workflow_transition

try:
    from django.urls import reverse_lazy
except ImportError as old_django:
    from django.core.urlresolvers import reverse_lazy


from django.views.decorators.cache import never_cache


__author__ = 'yaseen'


def protected(view_func):
    """
    ensure the view is not cached AND requires login
    """
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        response = never_cache(login_required(view_func))(request, *args, **kwargs)
        return response
    return _wrapped_view_func


urlpatterns = [
    url(r'^$', protected(MyFacetedSearchView()), name='haystac'),
    url(r'^add/$', CaseReportFormView.as_view(), name='add_casereport'),
    url(r'^autocomplete/$', AutoCompleteView.as_view(), name='autocomplete'),
    url(r'^formtype/$', FormTypeView.as_view(), name='ftype'),
    url(
        r'^(?P<case_id>[0-9]*)/(?P<title_slug>.*)/$',
        CaseReportDetailView.as_view(), name='casereport_detail',
    ),
    url(r'^download/(?P<file_id>.*)/$', downloadfile, name='download'),
    url(
        r'^edit/(?P<case_id>[0-9]*)/$',
        never_cache(CaseReportEditView.as_view()),
        name='edit'
    ),
    url(r'^(?P<pk>[0-9]*)/review$', ReviewDetailView.as_view(), name='review'),
]

# workflow transition view
urlpatterns += [
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name="casereport_workflow_transition")
]

# re-register Workflow Action names
urlpatterns += [
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Author Review Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Admin Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Approve'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Submit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Publish'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Revise'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', protected(workflow_transition), name='Send Back'),
]
