from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^add/(?P<action_pk>\d+)/$', views.add_bookmark, name='bookmarks_add'),
]
