"""rlp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import RedirectView

from rlp.core import views
from rlp.sitemaps import sitemaps
from casereport.views import ajax_lookup

handler500 = 'rlp.core.views.server_error'

urlpatterns = [
    url(r'^healthcheck/$', views.healthcheck),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('rlp.accounts.urls')),
    url(r'^bibliography/', include('rlp.bibliography.share_urls')),
    url(r'^bookmarks/', include('rlp.bookmarks.urls')),
    url(r'^comments/', include('rlp.discussions.urls')),
    url(r'^search/', include('rlp.search.urls')),
    url(r'^sitemap\.xml$',
        sitemap,
        {'sitemaps': sitemaps}),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^casereport/', include('casereport.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^ajax_lookup/(?P<channel>[-\w]+)$',
        ajax_lookup,
        name='ajax_lookup'),
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^discussions/', include('rlp.discussions.urls_edit_delete')),
    url(r'^documents/', include('rlp.documents.urls')),
    url(r'^bibliography/', include('rlp.bibliography.urls')),
    url(
        r'^send/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<object_id>\d+)/$',
        views.SendToView.as_view(),
        name='sendto',
    ),
    url(r'^bookmark$', views.BookmarkView.as_view(), name='bookmark_content'),
    url(
        r'^remove_bookmark$',
        views.BookmarkRemoveView.as_view(),
        name='remove_bookmark',
    ),
    url(r'^', views.home, name='homepage'),
    url(r'^about/', views.about, name='about'),
    url(r'^', include('cms.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^500/$', views.server_error),
        url(r'^404/$', views.server_error, kwargs={'template': '404.html'}),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
