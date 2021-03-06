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
        max_length=250,
        required=False,
        help_text="PDF, Word Doc, Google Doc file types; max file size 2MB")
    url = forms.URLField(required=False)
    share_link = EmbedVideoFormField(help_text='YouTube URL', required=False)
    title = forms.CharField(max_length=400)
    description = forms.CharField(widget=CKEditorWidget())
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by('slug'),
        help_text='Start typing or select tag(s) in the list',
        required=False,
    )
    tags.widget.attrs['class'] = 'select2'
    new_tags = forms.CharField(
        max_length=400,
        required=False,
        help_text="Terms added here will be added as new tags in the system. \
                   Separate with commas.")
    copyright = forms.BooleanField(label=CLABEL, required=False)
    members = MemberListField(
        label='Sarcoma Central Members',
        help_text='Start typing or select member(s) in the list',
        choices=(),  # gets filled in by the view
        required=False,)
    groups = GroupListField(
        label='My Groups',
        help_text='Start typing or select group(s) in the list',
        choices=(),  # gets filled in by the view
        required=False,
    )
    to_dashboard = forms.BooleanField(
        label='',
        required=False,
        widget=forms.HiddenInput,
        initial=True,
    )
    doc_type = forms.CharField(
        label='',
        required=False,
        widget=forms.HiddenInput,
        initial='file',
    )


class BaseDocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['copyright'].label = CLABEL
        self.fields['description'].widget = CKEditorWidget()
        if Tag.objects.count():
            self.fields['tags'] = forms.ModelMultipleChoiceField(
                queryset=Tag.objects.order_by('slug'),
                required=False
            )
            self.fields['tags'].widget.attrs['class'] = 'select2'
        self.fields['new_tags'] = forms.CharField(
            max_length=400,
            required=False,
            help_text="Terms added here will be added as new tags in the system. \
                       Separate with commas.")

    class Meta:
        model = Document
        exclude = [
            'owner', 'date_added', 'date_updated', 'project', 'tags',
            'origin_id', 'origin_type',
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
            'origin_id', 'origin_type',
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
