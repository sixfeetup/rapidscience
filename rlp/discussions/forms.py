from django.conf import settings
from django import forms
from django_comments.forms import CommentForm as BaseCommentForm
from taggit.models import Tag
from ckeditor.widgets import CKEditorWidget

from rlp.core.forms import MemberListField, GroupListField
from rlp.discussions.models import ThreadedComment


class ThreadedCommentForm(BaseCommentForm):
    comment = forms.CharField(
        label='Comment',
        widget=CKEditorWidget(),)
    reply_to = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        comment = kwargs.pop("comment", None)
        if comment:
            initial = kwargs.pop("initial", {})
            initial.update({"reply_to": comment.pk})
            kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        if self.initial['content_type'] == 'projects.project':
            self.fields['title'] = forms.CharField(label='Title', required=True)
        if comment:
            self.fields['comment'].widget.attrs['id'] = "editor-" + str(comment.pk)

    def get_comment_model(self):
        return ThreadedComment

    def get_comment_create_data(self):
        data = super().get_comment_create_data()
        data.update({
            'title': self.cleaned_data.get('title', ''),
            'thread_id': 0,
            'level': 0,
            'order': 1,
            'parent_id': self.cleaned_data['reply_to'],
        })
        return data


class ThreadedCommentEditForm(forms.ModelForm):
    comment = forms.CharField(
        label='Comment',
        widget=CKEditorWidget(),
    )

    class Meta:
        model = ThreadedComment
        fields = ['comment']


class ThreadedCommentWithTitleEditForm(forms.ModelForm):
    title = forms.CharField(label='Title', required=True)
    comment = forms.CharField(
        label='Comment',
        widget=CKEditorWidget(),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        help_text='Separate tags with commas',
        required=False,
    )
    tags.widget.attrs['class'] = 'select2'

    class Meta:
        model = ThreadedComment
        fields = ['title', 'comment', 'tags']


internal_member_field = MemberListField(
    label='Members',
    help_text='Separate names with commas',
    choices=(),  # gets filled in by the view
    required=False,
)
group_field = GroupListField(
    label='My Groups',
    help_text='Separate names with commas',
    choices=(),  # gets filled in by the view
    required=False,
)


class NewDiscussionForm(forms.Form):
    discussion_title = forms.CharField(label='Title', required=True)
    discussion_body = forms.CharField(widget=CKEditorWidget(),)
    members = internal_member_field
    groups = group_field
    to_dashboard = forms.BooleanField(
        label='',
        required=False,
        widget=forms.HiddenInput,
        initial=True,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        help_text='Separate tags with commas',
        required=False,
    )
    tags.widget.attrs['class'] = 'select2'

    field_order = ['discussion_title', 'discussion_body', 'members',
                   'groups', 'tags']
