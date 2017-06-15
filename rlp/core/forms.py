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


def group_choices(user):
    '''
    return (ID, name) pairs for any group where
      * the user is in the group
    '''
    if not user:
        return
    for group in user.active_projects():
        yield (group.id, group.title)


member_choice_field = MemberListField(
    label='Members',
    help_text='Type name; separate with commas',
    choices=(),  # override this in the view with member_choices()
    required=False,
)

group_choice_field = GroupListField(
    label='Groups',
    help_text='Type name; separate with commas',
    choices=(),  # override this in the view with group_choices()
    required=False,
)


class SendToForm(forms.Form):
    to_dashboard = forms.BooleanField(
        label='My Dashboard',
        required=False,
    )
    groups = group_choice_field
    members = member_choice_field
    comment = forms.CharField(
        label='Message',
        widget=forms.Textarea,
        required=False,
    )
    field_order = ['to_dashboard', 'members', 'groups', 'comment']


def get_sendto_form(user, content, type_key, data=None):
    '''populate a SendToForm with appropriate choices'''

    form = SendToForm(data)
    form.label_suffix = ''
    form.fields['groups'].choices = group_choices(user)
    form.fields['members'].choices = member_choices()
    if user in content.get_viewers():
        # don't show the checkbox if the user already has this content
        form.fields['to_dashboard'].widget = forms.HiddenInput()
    else:
        # customize the text of the checkbox
        dest = settings.TYPE_DISPLAY_NAMES.get(type_key, '')
        form.fields['to_dashboard'].label = 'My Dashboard {}'.format(dest)
    return form
