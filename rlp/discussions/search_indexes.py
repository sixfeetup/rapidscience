from django.template.loader import render_to_string
from haystack import indexes

from rlp.search.search_indexes import TaggableBaseIndex

from .models import ThreadedComment


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

    def index_queryset(self, using=None):
        """ limit discussion object to non-editorial
        """
        qs = super(CommentIndex, self).index_queryset(using=using)
        qs = qs.filter(is_public=True, is_removed=False)

        # can;t do this because it's a property
        # qs = qs.exclude(is_editorial_note=True)
        qs = qs.exclude(id__in=(o.id for o in qs if o.is_editorial_note))
        return qs
