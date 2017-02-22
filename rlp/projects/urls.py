from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.projects_list, name='projects_list'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/$',
        views.projects_detail,
        {'tab': 'activity'},
        name='projects_detail'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/documents/$',
        views.projects_detail,
        {'tab': 'documents'},
        name='projects_documents'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/discussions/$',
        views.projects_detail,
        {'tab': 'discussions'},
        name='projects_discussions'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/casereports/$',
        views.projects_detail,
        {'tab': 'casereports'},
        name='projects_casereports'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/bibliography/$',
        views.projects_detail,
        {'tab': 'bibliography'},
        name='projects_bibliography'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/members/$',
        views.projects_members,
        name='projects_members'),
]
