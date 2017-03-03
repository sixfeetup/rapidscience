from django import forms
from django.core.validators import EmailValidator


class CommaSeparatedEmailField(forms.Field):
    def __init__(
        self, dedup=True, max_length=None, min_length=None,
        *args, **kwargs
    ):
        super(CommaSeparatedEmailField, self).__init__(*args, **kwargs)
        self.validators.append(EmailValidator())

    def to_python(self, value):
        return list({addr.strip() for addr in value.split(',')})

    def clean(self, value):
        addrs = self.to_python(value)
        for addr in addrs:
            self.validate(addr)
            self.run_validators(addr)
        return addrs


class InviteForm(forms.Form):
    internal = forms.MultipleChoiceField(
        label='Invite Rapid Science Members',
        help_text='Type name; separate with commas',
        choices=(),  # gets filled in by the view
        required=False,
    )
    external = CommaSeparatedEmailField(
        label='Invite Non-members',
        help_text='Enter institutional e-mails; separate with commas',
        required=False,
    )
    invitation_message = forms.CharField(
        widget=forms.Textarea,
    )


class NewGroupForm(forms.Form):
    group_choices = (
        (0, 'Open - All validated Rapid Science members can view activity and join to participate'),
        (1, 'Closed - Moderator must approve / invite members'))

    group_name = forms.CharField(max_length=200)
    about = forms.CharField(max_length=300, widget=forms.Textarea)
    banner_image = forms.ImageField()
    approval = forms.ChoiceField(
        widget=forms.RadioSelect, choices=group_choices)
