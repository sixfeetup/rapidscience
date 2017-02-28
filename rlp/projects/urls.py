from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.projects_list, name='projects_list'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/$',
        views.projects_detail,
        {'tab': 'activity'},
        name='projects_detail'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/(?P<tab>\w+)/$',
        views.projects_detail,
        name='projects_tab'),
    url(r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/members/$',
        views.projects_members,
        name='projects_members'),
    url(
        r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/invite$',
        views.invite_members,
        name='projects_invite',
    ),
    url(
        r'^(?P<pk>\d+)/join$',
        views.JoinGroup.as_view(),
        name='projects_join',
    )
]
