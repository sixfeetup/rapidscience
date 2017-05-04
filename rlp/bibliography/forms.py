from django import forms
from django.utils.timezone import now

from taggit.models import Tag

from . import choices
from .models import (
    get_or_create_reference,
    parse_user_submission,
    Reference,
    ReferenceShare,
)
from rlp.projects.models import Project


class SearchForm(forms.Form):
    q = forms.CharField(required=False)

    def clean(self):
        data = self.cleaned_data
        self.results = []
        query = data.get('q')
        if query:
            self.results = get_or_create_reference(query)


class ReferenceShareForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Project.objects.order_by('title')

    class Meta:
        model = ReferenceShare
        fields = [
            'group',
            'recipients',
            'comment',
        ]
        widgets = {
            'recipients': forms.SelectMultiple(attrs={'class': 'chosen-select'}),
            'comment': forms.Textarea(attrs={'cols': 80, 'rows': 5, 'class': 'remaining-characters'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        recipients = cleaned_data.get('recipients')
        if not any([group, recipients]):
            raise forms.ValidationError('You must select at least one recipient or group.')


class BaseReferenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Tag.objects.count():
            self.fields['tags'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple(),
                queryset=Tag.objects.all(),
                required=False
            )

    publication_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    authors = forms.CharField(max_length=255,
                              help_text='List all authors separated by a comma e.g. "Smith J, Jones S".')
    url = forms.URLField(required=False)

    class Meta:
        model = Reference
        fields = [
            'title',
            'publication_date',
            'authors',
            'upload',
            'url',
        ]

    def clean(self):
        cleaned_data = super().clean()
        upload = cleaned_data.get('upload')
        url = cleaned_data.get('url')
        if not any([upload, url]):
            raise forms.ValidationError('Please provide a link or upload a file.')

    def save(self, commit=True):
        self.cleaned_data['reference_type'] = self.reference_type
        reference = super().save(commit=False)
        reference.source = choices.MEMBER
        modified_cleaned_data = self.cleaned_data.copy()
        # Remove tags before attempting to serialize to JSON
        modified_cleaned_data.pop('tags', None)
        # Remove file uploads before attempting to serialize to JSON, we'll set the correct url after we've saved the
        # instance first.
        modified_cleaned_data.pop('upload', None)
        reference.raw_data = modified_cleaned_data
        reference.parsed_data = parse_user_submission(modified_cleaned_data)
        # Save now that we've set the raw and parsed data:
        reference.save()
        # If there is an upload, we need to set the url manually so that it is the correct url.
        # A duplicate file name will have a hash added to the file name post-save.
        # If we grab the url before save, we'll be pointing at the original file and not the file currently being
        # uploaded e.g. my_file.pdf vs my_file_rHbQNi7.pdf.
        if reference.upload:
            reference.parsed_data['upload_url'] = reference.upload.url
            reference.save()
        return reference


class BookForm(BaseReferenceForm):
    reference_type = choices.BOOK
    editors = forms.CharField(max_length=255,
                              required=False,
                              help_text='List all editors separated by a comma e.g. "Smith J, Jones S".')
    publication_date = forms.IntegerField(max_value=now().year + 5, min_value=1500)
    pages = forms.IntegerField(min_value=1, label='# pages')
    publisher = forms.CharField(max_length=255, required=False)
    isbn = forms.CharField(max_length=15, label='ISBN', required=False)

    class Meta(BaseReferenceForm.Meta):
        fields = [
            'title',
            'publication_date',
            'pages',
            'authors',
            'editors',
            'publisher',
            'isbn',
            'upload',
            'url',
        ]


class BookSectionForm(BaseReferenceForm):
    reference_type = choices.BOOK_SECTION
    book_title = forms.CharField(max_length=255, label='Book title')
    publication_date = forms.IntegerField(max_value=now().year + 5, min_value=1500)
    page_range = forms.CharField(max_length=20)
    editors = forms.CharField(max_length=255,
                              required=False,
                              help_text='List all editors separated by a comma e.g. "Smith J, Jones S".')

    publisher = forms.CharField(max_length=255, required=False)
    isbn = forms.CharField(max_length=15, label='ISBN', required=False)

    class Meta(BaseReferenceForm.Meta):
        fields = [
            'title',
            'book_title',
            'publication_date',
            'page_range',
            'authors',
            'editors',
            'publisher',
            'isbn',
            'pubmed_id',
            'doi',
            'upload',
            'url',
        ]


class JournalArticleForm(BaseReferenceForm):
    reference_type = choices.JOURNAL_ARTICLE
    publication_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    journal_title = forms.CharField(max_length=255)
    journal_volume = forms.CharField(max_length=100, required=False)
    journal_issue = forms.CharField(max_length=20, required=False)
    page_range = forms.CharField(max_length=20, required=False)

    class Meta(BaseReferenceForm.Meta):
        fields = [
            'title',
            'publication_date',
            'journal_title',
            'journal_volume',
            'journal_issue',
            'page_range',
            'authors',
            'pubmed_id',
            'doi',
            'upload',
            'url',
        ]

    def clean_publication_date(self):
        data = self.cleaned_data['publication_date']
        if data:
            return data.strftime('%d %b %Y')
        return data


class ProjectReferenceForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        fields = [
            'tags'
        ]
        model = Reference

