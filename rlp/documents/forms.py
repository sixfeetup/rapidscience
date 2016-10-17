from django import forms

from taggit.models import Tag

from .models import Document, File, Image, Link, Video


class BaseDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Tag.objects.count():
            self.fields['tags'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple(),
                queryset=Tag.objects.all(),
                required=False
            )

    class Meta:
        model = Document
        exclude = [
            'owner', 'date_added', 'date_updated', 'project', 'tags',
        ]


class FileForm(BaseDocumentForm):
    class Meta:
        model = File
        exclude = [
            'owner', 'date_added', 'date_updated', 'project', 'tags',
        ]


class ImageForm(BaseDocumentForm):
    class Meta:
        model = Image
        exclude = [
            'owner', 'date_added', 'date_updated', 'project', 'height', 'width', 'tags',
        ]


class LinkForm(BaseDocumentForm):
    class Meta:
        model = Link
        fields = [
            'title', 'url', 'description',
        ]


class VideoForm(BaseDocumentForm):
    class Meta:
        model = Video
        fields = [
            'title', 'share_link', 'description',
        ]
