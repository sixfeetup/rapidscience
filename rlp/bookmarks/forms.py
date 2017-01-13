from django import forms

from .models import Bookmark, Folder


class BookmarkForm(forms.ModelForm):
    class Meta:
        fields = [
            'folder',
            'name',
            'content_type',
            'object_pk',
        ]
        model = Bookmark
        widgets = {
            'content_type': forms.HiddenInput(),
            'object_pk': forms.HiddenInput(),
            'folder': forms.HiddenInput(),
        }


class UpdateBookmarkForm(forms.ModelForm):
    class Meta:
        fields = [
            'folder',
            'name',
        ]
        model = Bookmark
        widgets = {
            'folder': forms.HiddenInput(),
        }


class BookmarkFolderForm(forms.ModelForm):
    class Meta:
        fields = ['name', ]
        model = Folder
