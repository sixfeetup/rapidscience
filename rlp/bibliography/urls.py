from django.conf.urls import url

from . import views


app_name = 'bibliography'
urlpatterns = [
    url(r'search/$', views.reference_search, name='reference_search'),
    url(r'add/book/$', views.add_book, name='add_book'),
    url(r'add/book-chapter/$', views.add_book_chapter, name='add_book_chapter'),
    url(r'add/article/$', views.add_article, name='add_article'),
    url(r'(?P<reference_pk>\d+)/$', views.reference_detail, name='reference_detail'),
    url(r'(?P<reference_pk>\d+)/add/$', views.reference_add, name='reference_add'),
    url(r'(?P<reference_pk>\d+)/edit/$', views.reference_edit, name='reference_edit'),
    url(r'(?P<reference_pk>\d+)/delete/$', views.reference_delete, name='reference_delete'),
]
