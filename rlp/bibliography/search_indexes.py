from haystack import indexes

from .models import Reference, UserReference
from rlp.search.search_indexes import BaseIndex, TaggableBaseIndex


class ReferenceIndex(TaggableBaseIndex, indexes.Indexable):

    def prepare_tags(self, obj):
        tags =  [tag.id for tag in obj.tags.all()]
        urefs = UserReference.objects.filter(reference=obj)
        for uref in urefs:
            tags.extend([tag.id for tag in uref.tags.all()])
        return {*tags}

    def prepare_title(self, obj):
        return "{}".format(obj.title)

    def get_model(self):
        return Reference

    def index_queryset(self, using=None):
        user_refs = UserReference.objects.all()
        return Reference.objects.filter( id__in=[ur.reference_id for ur in user_refs])
