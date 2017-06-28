from haystack import indexes

from .models import Reference
from rlp.search.search_indexes import BaseIndex


class ReferenceIndex(BaseIndex):
    def prepare_title(self, obj):
        return "{}".format(obj.title)

    def get_model(self):
        return Reference

