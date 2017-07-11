from haystack import indexes

from .models import Reference, UserReference
from rlp.search.search_indexes import BaseIndex, TaggableBaseIndex


class ReferenceIndex(TaggableBaseIndex, indexes.Indexable):

    def prepare_title(self, obj):
        return "{}".format(obj.reference.title)

    def get_model(self):
        return UserReference

    def index_queryset(self, using=None):
        user_refs = UserReference.objects.all()
        return user_refs
