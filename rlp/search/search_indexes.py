from django.template.loader import render_to_string
from haystack import indexes


class BaseIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    link = indexes.CharField()

    def prepare_title(self, obj):
        return obj.title

    def prepare_link(self, obj):
        return obj.get_absolute_url()

    def prepare_text(self, obj):
        searchstring = render_to_string(
            'search/_text.txt',
            {'object': obj, })
        return searchstring


class TaggableBaseIndex(BaseIndex):
    tags = indexes.MultiValueField()
    mtags = indexes.MultiValueField()

    def prepare_tags(self, obj):
        return [tag.id for tag in obj.tags.all()]

    def prepare_mtags(self, obj):
        return [mtag.id for mtag in obj.mtags.all()]
