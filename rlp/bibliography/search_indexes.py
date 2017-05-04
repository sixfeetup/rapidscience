from haystack import indexes

from .models import Reference
from rlp.search.search_indexes import TaggableBaseIndex


class ReferenceIndex(TaggableBaseIndex, indexes.Indexable):
    def prepare_title(self, obj):
        return "{}".format(obj.title)

    def get_model(self):
        return Reference

