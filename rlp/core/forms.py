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


def member_choices(user, content=None):
    '''return (ID, name) pairs for any member not viewing this content'''
    current = []
    if content:
        current = [
            vwr for vwr in content.get_viewers()
            if not hasattr(vwr, 'users')  # skip groups
        ]
    for member in User.objects.all():
        if member == user or member in current:
            continue
        yield (member.id, member.get_full_name())


def group_choices(user, content=None, came_from=0):
    '''
    return (ID, name) pairs for any group where
      * the user is in the group
      * the group is open (or is where content originated)
      * the group is not already viewing this content
    '''
    try:
        came_from = int(came_from)
    except TypeError:
        pass
    if not user and not content:
        return
    for group in user.active_projects():
        if group.approval_required and group.id != came_from:
            continue
        if content and group in content.get_viewers():
            continue
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


def get_sendto_form(user, content, type_key, data=None):
    '''populate a SendToForm with appropriate choices'''

    form = SendToForm(data)
    form.fields['groups'].choices = group_choices(user, content)
    form.fields['members'].choices = member_choices(user, content)
    if user in content.get_viewers():
        # don't show the checkbox if the user already has this content
        form.fields['to_dashboard'].widget = forms.HiddenInput()
    else:
        # customize the text of the checkbox
        dest = settings.TYPE_DISPLAY_NAMES.get(type_key, '')
        form.fields['to_dashboard'].label = 'My Dashboard {}'.format(dest)
    return form
