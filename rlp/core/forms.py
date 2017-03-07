from django import forms

from rlp.accounts.models import User


def member_choices(content):
    '''return (ID, name) pairs for any member not viewing this content'''
    if content:
        current = [
            vwr for vwr in content.get_viewers()
            if not hasattr(vwr, 'users')  # skip groups
        ]
        for user in User.objects.all():
            if user in current:
                continue
            yield (user.id, user.get_full_name())


def group_choices(user, content):
    '''
    return (ID, name) pairs for any group where
      * the user is in the group
      * the group is not already viewing this content
    '''
    if user and content:
        for group in user.active_projects():
            if group in content.get_viewers():
                continue
            yield (group.id, group.title)


member_choice_field = forms.MultipleChoiceField(
    label='Members',
    help_text='Type name; separate with commas',
    choices=(),  # override this in the view with member_choices()
    required=False,
)

group_choice_field = forms.MultipleChoiceField(
    label='Groups',
    help_text='Type name; separate with commas',
    choices=(),  # override this in the view with group_choices()
    required=False,
)


class SendToForm(forms.Form):
    groups = group_choice_field
    members = member_choice_field


def get_sendto_form(user, content, data=None):
    '''populate a SendToForm with appropriate choices'''

    form = SendToForm(data)
    form.fields['groups'].choices = group_choices(user, content)
    form.fields['members'].choices = member_choices(content)
    return form
