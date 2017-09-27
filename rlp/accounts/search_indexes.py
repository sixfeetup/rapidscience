from haystack import indexes
from django.template.loader import render_to_string

from .models import User

from rlp.search.search_indexes import BaseIndex


class UserIndex(BaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_staff=False, is_active=True)

    def prepare_title(self, obj):
        title = obj.get_full_name()
        if obj.degrees:
            title += ', {}'.format(obj.degrees)
        return title

    def prepare_text(self, obj):
        searchstring = render_to_string(
            'search/indexes/accounts/user_text.txt',
            {'object': obj, })
        return searchstring
