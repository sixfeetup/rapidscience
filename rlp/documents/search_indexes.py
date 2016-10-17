from haystack import indexes

from .models import File, Image, Link, Video
from rlp.search.search_indexes import TaggableBaseIndex


class FileIndex(TaggableBaseIndex, indexes.Indexable):
    display_type = indexes.CharField()

    def get_model(self):
        return File

    def prepare_display_type(self, obj):
        return obj.display_type

    def prepare(self, obj):
        self.prepared_data = super().prepare(obj)
        backend = self._get_backend(None)
        text = backend.extract_file_contents(obj.upload.path)
        self.prepared_data['text'] += "\n {}".format(text)
        return self.prepared_data


class LinkIndex(TaggableBaseIndex, indexes.Indexable):
    def get_model(self):
        return Link


class ImageIndex(TaggableBaseIndex, indexes.Indexable):
    display_type = indexes.CharField()

    def get_model(self):
        return Image

    def prepare_display_type(self, obj):
        return obj.display_type


class VideoIndex(TaggableBaseIndex, indexes.Indexable):
    def get_model(self):
        return Video
