from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^delete/(?P<comment_pk>\d+)/$', views.comment_delete, name='comments-delete'),
    url(r'^edit/(?P<comment_pk>\d+)/$', views.comment_edit, name='comments-edit'),
    url(r'^(?P<comment_pk>\d+)/$', views.comment_detail, name='comments-detail'),
]
