from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^post/$', views.comment_post, name='comments-post-comment'),
    url(r'^posted/$', views.comment_done, name='comments-comment-done'),
    url(r'^cr/(\d+)/(.+)/$', views.post_redirect, name='comments-url-redirect'),
]
