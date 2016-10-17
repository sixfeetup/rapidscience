from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<reference_pk>\d+)/share/$', views.reference_share, name='reference_share'),
]
