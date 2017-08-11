from haystack import indexes

from .models import Project
from rlp.search.search_indexes import BaseIndex


class ProjectIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return Project

    def prepare_title(self, obj):
        return obj.title

    def prepare_text(self, obj):
        return obj.goal
