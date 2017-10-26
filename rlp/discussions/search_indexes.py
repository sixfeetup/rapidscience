import bleach

from django.template.loader import render_to_string

from haystack import indexes

from .models import ThreadedComment
from rlp.search.search_indexes import TaggableBaseIndex


class CommentIndex(TaggableBaseIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    comment = indexes.CharField()

    def get_model(self):
        return ThreadedComment

    def prepare_text(self, obj):
        searchstring = render_to_string(
            'search/indexes/discussions/threadedcomment_text.txt',
            {'object': obj, })
        return searchstring

    def prepare_title(self, obj):
        return obj.title
