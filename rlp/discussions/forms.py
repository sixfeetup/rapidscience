from django.conf import settings
from django import forms
from django_comments.forms import CommentForm as BaseCommentForm

from rlp.discussions.models import ThreadedComment


class ThreadedCommentForm(BaseCommentForm):
    comment = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'class': 'remaining-characters'}),
                              max_length=settings.COMMENT_MAX_LENGTH,)
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
        widget=forms.Textarea(attrs={'class': 'remaining-characters'}),
        max_length=settings.COMMENT_MAX_LENGTH
    )

    class Meta:
        model = ThreadedComment
        fields = ['comment']


class ThreadedCommentWithTitleEditForm(forms.ModelForm):
    title = forms.CharField(label='Title', required=True)
    comment = forms.CharField(
        label='Comment',
        widget=forms.Textarea(attrs={'class': 'remaining-characters'}),
        max_length=settings.COMMENT_MAX_LENGTH
    )

    class Meta:
        model = ThreadedComment
        fields = ['title', 'comment']
