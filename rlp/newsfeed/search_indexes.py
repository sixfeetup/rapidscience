from haystack import indexes

from .models import NewsItem
from rlp.search.search_indexes import BaseIndex


class NewsItemIndex(BaseIndex, indexes.Indexable):
    def get_model(self):
        return NewsItem

    def index_queryset(self, using=None):
        return self.get_model().published.all()

    def prepare_link(self, obj):
        return obj.url

