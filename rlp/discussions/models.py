from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Max, Min
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from collections import OrderedDict

from rlp.accounts.models import User
from rlp.core.models import SharedObjectMixin
from rlp.projects.models import Project


def max_thread_level_for_content_type(content_type):
    app_model = "%s.%s" % (content_type.app_label, content_type.model)
    if app_model in settings.COMMENTS_MAX_THREAD_LEVEL_BY_APP_MODEL:
        return settings.COMMENTS_MAX_THREAD_LEVEL_BY_APP_MODEL[app_model]
    else:
        return settings.COMMENTS_MAX_THREAD_LEVEL


class MaxThreadLevelExceededException(Exception):
    def __init__(self, content_type=None):
        self.max_by_app = max_thread_level_for_content_type(content_type)

    def __str__(self):
        return "Can not post comments over the thread level {}".format(self.max_by_app)


class ThreadedCommentManager(models.Manager):
    def for_app_models(self, *args):
        """Return ThreadedComments for pairs "app.model" given in args"""
        content_types = []
        for app_model in args:
            app, model = app_model.split(".")
            content_types.append(ContentType.objects.get(app_label=app,
                                                         model=model))
        return self.for_content_types(content_types)

    def for_content_types(self, content_types):
        qs = self.get_queryset().filter(content_type__in=content_types).reverse()
        return qs


class ThreadedComment(Comment, SharedObjectMixin):
    title = models.CharField(max_length=255, blank=True)
    thread_id = models.IntegerField(default=0, db_index=True)
    parent_id = models.IntegerField(default=0)
    level = models.SmallIntegerField(default=0)
    order = models.IntegerField(default=1, db_index=True)

    objects = ThreadedCommentManager()

    class Meta:
        ordering = ('-thread_id', 'order')
        verbose_name = 'comment'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if not self.parent_id:
                self.parent_id = self.id
                self.thread_id = self.id
            else:
                if max_thread_level_for_content_type(self.content_type):
                    with atomic():
                        self._calculate_thread_data()
                else:
                    raise MaxThreadLevelExceededException(self.content_type)
            kwargs["force_insert"] = False
            with atomic():
                if (
                    self.id == self.parent_id and
                    (isinstance(self.content_object, Project) or
                     isinstance(self.content_object, User))
                ):
                    # attach to the site instead of a member or group
                    site_type = ContentType.objects.get_for_model(Site)
                    self.content_type = site_type
                    self.content_object = Site.objects.get_current()
                super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete children
        for comment in self.children():
            # delete each individually
            # mass deletion using to_delete skips this custom method
            comment.delete()
        super(ThreadedComment, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('comments-detail', kwargs={
            'comment_pk': self.discussion_root.pk
        })

    def _calculate_thread_data(self):
        # Implements the following approach:
        #  http://www.sqlteam.com/article/sql-for-threaded-discussion-forums
        parent = ThreadedComment.objects.get(pk=self.parent_id)
        if parent.level == max_thread_level_for_content_type(self.content_type):
            raise MaxThreadLevelExceededException(self.content_type)

        self.thread_id = parent.thread_id
        self.level = parent.level + 1
        qc_eq_thread = ThreadedComment.objects.filter(thread_id=parent.thread_id)
        qc_ge_level = qc_eq_thread.filter(level__lte=parent.level,
                                          order__gt=parent.order)
        if qc_ge_level.count():
            min_order = qc_ge_level.aggregate(Min('order'))['order__min']
            ThreadedComment.objects.filter(thread_id=parent.thread_id, order__gte=min_order).update(order=F('order')+1)
            self.order = min_order
        else:
            max_order = qc_eq_thread.aggregate(Max('order'))['order__max']
            self.order = max_order + 1

    def allow_thread(self):
        if self.level < max_thread_level_for_content_type(self.content_type):
            return True
        else:
            return False

    def get_edit_url(self):
        return reverse('comments-edit', kwargs={
            'comment_pk': self.pk
        })

    def get_delete_url(self):
        return reverse('comments-delete', kwargs={
            'comment_pk': self.pk
        })

    @property
    def display_type(self):
        if self.is_reply():
            return 'Reply'
        return 'Comment'

    def is_reply(self):
        if self.content_type.name.lower() == 'comment':
            return True
        return False

    @property
    def is_discussion(self):
        '''stand-alone discussion, or comments on other content?'''
        # stand-alone discussions are attached to the site
        return self.content_object == Site.objects.get_current()

    def children(self):
        children = ThreadedComment.objects.filter(
            parent_id=self.id
        ).exclude(id=self.id)
        return children

    @property
    def discussion_root(self):
        if self.thread_id == 0:
            return self
        return ThreadedComment.objects.get(id=self.thread_id)

    def get_viewers(self):
        '''override to get the viewers for the discussion'''
        top_comment = self.discussion_root
        refs = top_comment._related.select_related('viewer_type').all()
        od = OrderedDict.fromkeys([r.viewer for r in refs])
        return od.keys()
