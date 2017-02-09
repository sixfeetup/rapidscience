from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .forms import PasswordResetForm
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^bookmarks/$',
        views.dashboard,
        {'tab': 'bookmarks'},
        name='dashboard_bookmarks'),
    url(r'^login/$',
        views.login,
        name='login'),
    url(r'^logout/$',
        views.logout,
        {'template_name': 'accounts/logged_out.html'},
        name='logout'),

    url(r'^password_change/$',
        auth_views.password_change,
        {'template_name': 'accounts/password_change_form.html',
         'extra_context': {'current_page': 'password_change'}},
        name='password_change'),

    url(r'^password_change/done/$',
        auth_views.password_change_done,
        {'template_name': 'accounts/password_change_done.html'},
        name='password_change_done'),

    url(r'^password_reset/$',
        auth_views.password_reset,
        {'template_name': 'accounts/password_reset_form.html',
         'email_template_name': 'emails/password_reset.txt',
         'html_email_template_name': 'emails/password_reset.html',
         'password_reset_form': PasswordResetForm},
        name='password_reset'),

    url(r'^password_reset/done/$',
        auth_views.password_reset_done,
        {'template_name': 'accounts/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'template_name': 'accounts/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^reset/done/$',
        auth_views.password_reset_complete,
        {'template_name': 'accounts/password_reset_complete.html'},
        name='password_reset_complete'),

    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        views.ActivationView.as_view(),
        name='registration_activate'),
    url(r'^profile/$', views.profile_edit, name='profile_edit'),
    url(r'^profile/(?P<pk>\d+)/$',
        views.profile,
        name='profile'),
    url(r'^profile/(?P<pk>\d+)/(?P<tab>\w+)/$',
        views.profile,
        name='profile_tab'),
]
