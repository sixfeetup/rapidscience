from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Max, Min
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType

from django_comments.models import Comment


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


class ThreadedComment(Comment):
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
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete children
        for comment in self.children():
            # delete each individually
            # mass deletion using to_delete skips this custom method
            comment.delete()
        super(ThreadedComment, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        if self.content_type.name == 'project':
            project = ThreadedComment.get_project_for_comment(self)
            return reverse('comments-detail', kwargs={
                'comment_pk': self.pk
            })
        return super().get_absolute_url()

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

    @classmethod
    def get_project_for_comment(cls, instance):
        content_type = instance.content_type
        # Comment on a project
        if content_type.model == 'project':
            return instance.content_object
        # Comment on a document/biblio
        if hasattr(instance.content_object, 'project'):
            return instance.content_object.project
        # Replies
        return ThreadedComment.get_project_for_comment(instance.content_object)

    def get_edit_url(self):
        project = ThreadedComment.get_project_for_comment(self)
        return reverse('comments-edit', kwargs={
            'comment_pk': self.pk
        })

    def get_delete_url(self):
        project = ThreadedComment.get_project_for_comment(self)
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

    def children(self):
        children = ThreadedComment.objects.filter(
            parent_id=self.id
        ).exclude(id=self.id)
        return children
