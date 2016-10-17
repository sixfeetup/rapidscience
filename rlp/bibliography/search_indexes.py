from haystack import indexes

from .models import ProjectReference
from rlp.search.search_indexes import TaggableBaseIndex


class ReferenceIndex(TaggableBaseIndex, indexes.Indexable):
    def prepare_title(self, obj):
        return "{}".format(obj.reference.title)

    def get_model(self):
        return ProjectReference

