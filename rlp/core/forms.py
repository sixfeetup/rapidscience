from django import forms
from django.conf import settings

from rlp.accounts.models import User
from rlp.projects.models import Project


class MemberListField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(MemberListField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'select2'

    def clean(self, value):
        return User.objects.filter(id__in=value)


class GroupListField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super(GroupListField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'select2'

    def clean(self, value):
        return Project.objects.filter(id__in=value)


def member_choices():
    '''return (ID, name) pairs for all members'''
    for member in User.objects.all():
        yield (member.id, member.get_full_name())


def group_choices(user, exclude=[]):
    '''
    return (ID, name) pairs for any group where
      * the user is in the group
    '''
    if not user:
        return
    for group in user.active_projects():
        if group not in exclude:
            yield (group.id, group.title)


member_choice_field = MemberListField(
    label='Sarcoma Central Members',
    help_text='Start typing or select member(s) in the list',
    choices=(),  # override this in the view with member_choices()
    required=False,
)

group_choice_field = GroupListField(
    label='Groups',
    help_text='Start typing or select group(s) in the list',
    choices=(),  # override this in the view with group_choices()
    required=False,
)


class SendToForm(forms.Form):
    groups = group_choice_field
    members = member_choice_field
    comment = forms.CharField(
        label='Message',
        widget=forms.Textarea,
        required=False,
    )
    field_order = ['members', 'groups', 'comment']


def get_sendto_form(user, content, type_key, data=None):
    '''populate a SendToForm with appropriate choices'''

    form = SendToForm(data)
    form.label_suffix = ''
    form.fields['groups'].choices = group_choices(user)
    form.fields['members'].choices = member_choices()
    return form
