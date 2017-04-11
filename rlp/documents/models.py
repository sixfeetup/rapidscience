from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from embed_video.fields import EmbedVideoField
from polymorphic.models import PolymorphicModel
from taggit.managers import TaggableManager

from rlp.core.models import SharedObjectMixin
from rlp.discussions.models import ThreadedComment


class Document(PolymorphicModel, SharedObjectMixin):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    discussions = GenericRelation(
        ThreadedComment,
        object_id_field='object_pk',
    )

    tags = TaggableManager()
    copyright = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('documents:document_detail', kwargs={
            'doc_pk': self.id,
        })

    def get_edit_url(self):
        from django.core.urlresolvers import reverse
        return reverse('documents:document_edit', kwargs={
            'doc_pk': self.id,
        })

    def get_delete_url(self):
        from django.core.urlresolvers import reverse
        return reverse('documents:document_delete', kwargs={
            'doc_pk': self.id,
        })

    @property
    def display_type(self):
        if hasattr(self, 'upload'):
            if self.upload.path.endswith(('.doc', '.docx')):
                return "Document (Word)"
            elif self.upload.path.endswith(('.pdf',)):
                return "Document (pdf)"
            elif self.upload.path.endswith(('.ppt', '.pptx')):
                return "Slideshow (ppt)"
            elif self.upload.path.endswith(('.key',)):
                return "Slideshow (Keynote)"
            elif self.upload.path.endswith(('.txt',)):
                return "Document (txt)"
            elif self.upload.path.endswith(('.rtf',)):
                return "Document (rtf)"
            elif self.upload.path.endswith(('.xls', '.xlsx')):
                return "Spreadsheet (xls)"
            elif self.upload.path.endswith(('.csv',)):
                return "Spreadsheet (csv)"
            elif self.upload.path.endswith(('.jpg', '.jpeg')):
                return "Image (jpg)"
            elif self.upload.path.endswith(('.png',)):
                return "Image (png)"
            elif self.upload.path.endswith(('.gif',)):
                return "Image (gif)"
            elif self.upload.path.endswith(('.avi',)):
                return "Video (avi)"
            elif self.upload.path.endswith(('.mov',)):
                return "Video (mov)"
            elif self.upload.path.endswith(('.zip',)):
                return "Compressed File (zip)"
            return 'Document'

    def get_viewers(self):
        '''override to get the viewers for the main object'''
        doc_obj = Document.objects.non_polymorphic().get(id=self.id)
        refs = doc_obj._related.select_related('viewer_type').all()
        return [r.viewer for r in refs]


class File(Document):
    upload = models.FileField(upload_to="docs/%Y/%m/%d")


class Image(Document):
    upload = models.ImageField(upload_to="docs/images/%Y/%m/%d",
                               max_length=255,
                               height_field='height', width_field='width')
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()


class Video(Document):
    share_link = EmbedVideoField(help_text='YouTube URL')

    @property
    def display_type(self):
        return 'Video'


class Link(Document):
    url = models.URLField()

    @property
    def display_type(self):
        return 'Link'
