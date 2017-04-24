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


__author__ = 'yaseen'

urlpatterns = [
    url(r'^$', MyFacetedSearchView(), name='haystac'),
    url(
        r'^results/$',
        TemplateView.as_view(template_name="casereport/search_results.html"),
    ),
    url(r'^add/$', CaseReportFormView.as_view(), name='add_casereport'),
    url(r'^autocomplete/$', AutoCompleteView.as_view(), name='autocomplete'),
    url(r'^formtype/$', FormTypeView.as_view(), name='ftype'),
    url(
        r'^(?P<case_id>[0-9]*)/(?P<title_slug>.*)/$',
        CaseReportDetailView.as_view(), name='casereport_detail',
    ),
    url(r'^download/(?P<file_id>.*)/$', downloadfile, name='download'),
    url(
        r'^edit/(?P<case_id>[0-9]*)/(?P<token>.*)/$',
        CaseReportEditView.as_view(),
    ),
    url(r'^(?P<pk>[0-9]*)/review$', ReviewDetailView.as_view(), name='review'),
]
