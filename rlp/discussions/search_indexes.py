import bleach

from django.template.loader import render_to_string

from haystack import indexes

from .models import ThreadedComment
from rlp.search.search_indexes import TaggableBaseIndex


class CommentIndex(TaggableBaseIndex, indexes.Indexable):
    def get_model(self):
        return ThreadedComment

    def prepare_title(self, obj):
        action = obj.action_object_actions.first()
        title = render_to_string('actstream/_action_detail.html', context={'action': action})
        title = bleach.clean(title, strip=True, tags=[])
        return title
