from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^add/(?P<action_pk>\d+)/$', views.add_bookmark, name='bookmark_add'),
    url(r'^(?P<bookmark_pk>\d+)/update/$', views.update_bookmark, name='bookmark_update'),
    url(r'^(?P<bookmark_pk>\d+)/delete/$', views.delete_bookmark, name='bookmark_delete'),
    url(r'^folders/add/$', views.add_bookmark_folder, name='bookmark_folder_add'),
    url(r'^folders/(?P<folder_pk>\d+)/delete/$', views.delete_bookmark_folder, name='bookmark_folder_delete'),
]
