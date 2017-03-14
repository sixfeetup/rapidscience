from django import forms
from django.core.validators import EmailValidator

from rlp.core.forms import MemberListField


class CommaSeparatedEmailField(forms.Field):
    def __init__(
        self, dedup=True, max_length=None, min_length=None,
        *args, **kwargs
    ):
        super(CommaSeparatedEmailField, self).__init__(*args, **kwargs)
        self.validators.append(EmailValidator())

    def to_python(self, value):
        if value:
            return list({addr.strip() for addr in value.split(',')})
        else:
            return []

    def clean(self, value):
        addrs = self.to_python(value)
        for addr in addrs:
            self.validate(addr)
            self.run_validators(addr)
        return addrs


internal_member_field = MemberListField(
    label='Invite Rapid Science Members',
    help_text='Type name; separate with commas',
    choices=(),  # gets filled in by the view
    required=False,
)
external_member_field = CommaSeparatedEmailField(
    label='Invite Non-members',
    help_text='Enter institutional e-mails; separate with commas',
    max_length=400,
    required=False,
)


class InviteForm(forms.Form):
    internal = internal_member_field
    external = external_member_field
    invitation_message = forms.CharField(
        widget=forms.Textarea,
    )

static_invite_text = 'You are invited by [First Name, Last Name of \
moderator] to join the [Group Name] group in Sarcoma Central, a Rapid \
Science channel.\
\n\nAs a member of Sarcoma Central, you may view the Group \
page and click the Join button if you wish to be added to the Group. \
If you\'re not already a Rapid Science member, you must first register \
here. You will then be subscribed to Sarcoma Central, and directed to \
the [Group Name] page.'


class NewGroupForm(forms.Form):
    group_choices = (
        (0, ('Open - All validated Rapid Science members can'
             'view activity and join to participate')),
        (1, 'Closed - Moderator must approve / invite members'))

    group_name = forms.CharField(max_length=200)
    about = forms.CharField(max_length=300, widget=forms.Textarea)
    banner_image = forms.ImageField(required=False)
    approval = forms.ChoiceField(
        widget=forms.RadioSelect, choices=group_choices)
    internal = internal_member_field
    external = external_member_field
    initial_text = static_invite_text
    invitation_message = forms.CharField(
        max_length=600,
        widget=forms.Textarea,
        required=False,
        disabled=True,
        initial=initial_text,
    )
    custom_invite_message = forms.CharField(
        max_length=600,
        widget=forms.Textarea,
        required=False,
    )

    field_order = ['group_name', 'about', 'banner_image', 'approval',
                   'internal', 'external']
