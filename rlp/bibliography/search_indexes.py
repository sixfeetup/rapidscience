from django.template.loader import render_to_string
from haystack import indexes

from .models import UserReference
from rlp.search.search_indexes import TaggableBaseIndex


class ReferenceIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return UserReference

    def prepare(self, obj):
        prepared_data = super(ReferenceIndex, self).prepare(obj)
        return prepared_data

    def prepare_text(self, obj):
        searchstring = render_to_string(
            'search/indexes/bibliography/userreference_text.txt',
            {'object': obj,
             'data': obj.reference.parsed_data})
        return searchstring

    def prepare_title(self, obj):
        return "{}".format(obj.reference.title)

    def index_queryset(self, using=None):
        user_refs = UserReference.objects.all()
        return user_refs
