from django.conf.urls import url

from django_comments.views.comments import post_comment, comment_done

from . import views


urlpatterns = [
    url(r'^post/$', post_comment, name='comments-post-comment'),
    url(r'^posted/$', comment_done, name='comments-comment-done'),
    url(r'^cr/(\d+)/(.+)/$', views.post_redirect, name='comments-url-redirect'),
]
