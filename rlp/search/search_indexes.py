from haystack import indexes


class BaseIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField()
    link = indexes.CharField()

    def prepare_title(self, obj):
        return obj.title

    def prepare_link(self, obj):
        return obj.get_absolute_url()


class TaggableBaseIndex(BaseIndex):
    tags = indexes.MultiValueField()

    def prepare_tags(self, obj):
        return [tag.id for tag in obj.tags.all()]

