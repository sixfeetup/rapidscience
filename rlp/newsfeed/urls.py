from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.newsitem_list, name='newsitem_list'),
]
