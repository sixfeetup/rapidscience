from django import forms

from embed_video.fields import EmbedVideoFormField
from taggit.models import Tag
from ckeditor.widgets import CKEditorWidget

from rlp.core.forms import MemberListField, GroupListField
from .models import Document, File, Image, Link, Video

CLABEL = "Please check this box if you are not the copyright owner of \
           this material or if it is not under license for public \
           viewing. This will ensure that only validated participants \
           of this project can access it."


class AddMediaForm(forms.Form):
    upload = forms.FileField(
        required=False,
        help_text="PDF, Word Doc, Google Doc file types; max file size 2MB")
    url = forms.URLField(required=False)
    share_link = EmbedVideoFormField(help_text='YouTube URL', required=False)
    title = forms.CharField(max_length=400)
    description = forms.CharField(widget=CKEditorWidget())
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        help_text='Separate tags with commas',
        required=False,
    )
    tags.widget.attrs['class'] = 'select2'
    copyright = forms.BooleanField(label=CLABEL, required=False)
    members = MemberListField(
        label='Members',
        help_text='Type name; separate with commas',
        choices=(),  # gets filled in by the view
        required=False,)
    groups = GroupListField(
        label='My Groups',
        help_text='Separate names with commas',
        choices=(),  # gets filled in by the view
        required=False,
    )
    to_dashboard = forms.BooleanField(
        label='',
        required=False,
        widget=forms.HiddenInput,
        initial=True,
    )


class BaseDocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['copyright'].label = CLABEL
        if Tag.objects.count():
            self.fields['tags'] = forms.ModelMultipleChoiceField(
                queryset=Tag.objects.all(),
                required=False
            )
            self.fields['tags'].widget.attrs['class'] = 'select2'

    class Meta:
        model = Document
        exclude = [
            'owner', 'date_added', 'date_updated', 'project', 'tags',
        ]


class FileForm(BaseDocumentForm):
    class Meta:
        model = File
        fields = [
            'upload', 'title', 'description', 'copyright',
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
            'url', 'title', 'description', 'copyright',
        ]


class VideoForm(BaseDocumentForm):
    class Meta:
        model = Video
        fields = [
            'share_link', 'title', 'description', 'copyright',
        ]
