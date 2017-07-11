from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_text

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.forms import ModelSearchForm as BaseModelSearchForm
from haystack.query import SQ
from haystack.utils import get_model_ct

from taggit.models import Tag

from rlp.managedtags.models import ManagedTag
from rlp.projects.models import Project


EXCLUDE_MODELS = (
    'Title',
    'Post',
    'NewsItem'
)


def get_action_object_content_types():
    from rlp.bibliography.models import Reference
    from rlp.discussions.models import ThreadedComment
    from rlp.documents.models import File, Image, Video, Link
    from casereport.models import CaseReport
    choices = [
        ('', 'All'),
        (get_model_ct(ThreadedComment), 'Discussions'),
        (get_model_ct(CaseReport), 'Case Reports'),
        (get_model_ct(File), 'Documents'),
        (get_model_ct(Image), 'Images'),
        (get_model_ct(Video), 'Videos'),
        (get_model_ct(Link), 'Links'),
        (get_model_ct(Reference), 'References'),
    ]
    return choices


class ActionObjectForm(forms.Form):
    content_type = forms.ChoiceField(choices=get_action_object_content_types(), required=False)

    def clean_content_type(self):
        data = self.cleaned_data['content_type']
        if data:
            app_label, model = data.split('.')
            return ContentType.objects.get(app_label=app_label, model=model)


class ProjectChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.title[:50])


class ProjectContentForm(ActionObjectForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['user_activity_only'] = forms.BooleanField(
                label='Show only my activity',
                required=False,
            )
            if not user.can_access_all_projects:
                self.fields['project'].queryset = Project.objects.filter(approval_required=False)

    project = ProjectChoiceField(queryset=Project.objects.all(), required=False, empty_label='All Projects')


def model_choices(using=DEFAULT_ALIAS):
    choices = [
        [get_model_ct(m), smart_text(m._meta.verbose_name_plural).title()]
        for m in connections[using].get_unified_index().get_indexed_models()
        if m.__name__ not in EXCLUDE_MODELS
    ]
    for index, sublist in enumerate(choices):
        if sublist[1] == "Comments":
            choices[index][1] = "Discussions"
        if sublist[1] == "Projects":
            choices[index][1] = "Groups"
        if sublist[1] == "Raw References":
            choices[index][1] = "References"
    return sorted(choices, key=lambda x: x[1])


class ModelSearchForm(BaseModelSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # haystack.forms.ModelSearchForm assigns the `model` field in `__init__()`, so we have to do the same here to
        # override the `choices` callable.
        self.fields['models'] = \
            forms.MultipleChoiceField(choices=model_choices,
                                      required=False,
                                      label='Search In',
                                      widget=forms.CheckboxSelectMultiple)

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'placeholder': 'Search'
            }
        )
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.order_by('slug'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    mtags = forms.ModelMultipleChoiceField(
        queryset=ManagedTag.objects.order_by('slug'),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    def search(self):
        """
        SearchForm.search() & ModelSearchForm.search() have been combined here for easier readability and tweaking.
        This requires each SearchIndex to have a title and a body attribute.
        """
        if not self.is_valid():
            return self.no_query_found()
        query = self.cleaned_data.get('q')
        tags = self.cleaned_data.get('tags')
        mtags = self.cleaned_data.get('mtags')
        models = self.get_models()
        if not any([query, models, tags, mtags]):
            return self.no_query_found()
        sqs = self.searchqueryset
        if query:
            kwargs = {
                'fl': ['title','text'],
                'simple.pre': '<em class="highlighted">',
                'simple.post': '</em>'
            }
            # We search both title and text so we get the benefit of boosting title fields
            sqs = sqs.filter(
                SQ(title=query) | SQ(text=query)
            ).highlight(**kwargs)
        if models:
            sqs = sqs.models(*self.get_models())
        if tags:
            sqs = sqs.filter(tags__in=[tag.id for tag in tags])
        if mtags:
            sqs = sqs.filter(mtags__in=[mtag.id for mtag in mtags])
        return sqs
