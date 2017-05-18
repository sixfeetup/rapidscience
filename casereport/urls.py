from django.conf.urls import patterns, url
from django.views.generic import TemplateView

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

urlpatterns = [
    url(r'^$', MyFacetedSearchView(), name='haystac'),
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
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name="casereport_workflow_transition")
]

# re-register Workflow Action names
urlpatterns += [
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Author Review Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Admin Edit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Approve'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Submit'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Publish'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Revise'),
    url(r'^(?P<casereport_id>[0-9]*)/transition$', never_cache(workflow_transition), name='Send Back'),
]
