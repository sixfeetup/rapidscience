from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'add/document/$', views.add_document, name='add_document'),
    url(r'add/link/$', views.add_link, name='add_link'),
    url(r'add/video/$', views.add_video, name='add_video'),
    url(r'(?P<doc_pk>\d+)/$', views.document_detail, name='document_detail'),
    url(r'(?P<doc_pk>\d+)/edit/(?P<doc_type>\w+)/$', views.document_edit, name='document_edit'),
    url(r'(?P<doc_pk>\d+)/delete/$', views.document_delete, name='document_delete'),
]
