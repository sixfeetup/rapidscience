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
    ),
    url(
        r'^(?P<pk>\d+)/(?P<user>.*)/leave$',
        views.LeaveGroup.as_view(),
        name='projects_leave',
    ),
    url(
        r'^add/$',
        views.AddGroup.as_view(),
        name='projects_add',
    ),
    url(
        r'^(?P<pk>\d+)-(?P<slug>[\w\d-]+)/edit$',
        views.EditGroup.as_view(),
        name='projects_edit',
    ),
     url(
        r'^accept_membership/(?P<membership_id>\d+)/$',
        views.AcceptMembershipRequest.as_view(),
        name='accept_membership_request',
    ),
      url(
        r'^reject_membership/(?P<membership_id>\d+)/$',
        views.IgnoreMembershipRequest.as_view(),
        name='ignore_membership_request',
    ),
    url(
        r'^promote_to_moderator/(?P<membership_id>\d+)/$',
        views.PromoteToModerator.as_view(),
        name='promote_to_moderator',
    ),
    url(
        r'^demote_to_user/(?P<membership_id>\d+)/$',
        views.DemoteToMember.as_view(),
        name='demote_to_user',
    ),
 ]
