from haystack import indexes

from .models import File, Image, Link, Video
from rlp.search.search_indexes import TaggableBaseIndex


class FileIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    display_type = indexes.CharField()

    def get_model(self):
        return File

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        # this section throws an error during indexing
        # backend = self._get_backend(None)
        # if obj.upload.storage.exists( obj.upload.path ):
        #     text = backend.extract_file_contents(obj.upload.path)
        #     self.prepared_data['text'] += "\n {}".format(text)
        # else:
        #     print( "documents.models.File", obj, "is missing its actual file from", obj.upload.path)
        return self.prepared_data

    def prepare_display_type(self, obj):
        return obj.display_type


class LinkIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True)

    def get_model(self):
        return Link


class ImageIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    display_type = indexes.CharField()

    def get_model(self):
        return Image

    def prepare_display_type(self, obj):
        return obj.display_type


class VideoIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Video
