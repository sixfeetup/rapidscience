from django.conf import settings
from django import forms
from django.core.validators import EmailValidator

from rlp.core.forms import MemberListField

from django import forms
from django.utils.safestring import mark_safe

from ckeditor.widgets import CKEditorWidget


class SimpleImageWidget(forms.FileInput):
    def __init__(self, attrs={}):
        super(SimpleImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        #if settings.DEBUG:
        #    print("simpleImageWidget: name:", name)
        #    print("simpleImageWidget: value:", value)
        #    print("simpleImageWidget: attrs:", attrs)
        #    print("simpleImageWidget: self:", dir(self))
        output = []
        if value:
            output.append(('<img src="%s" style="height:160px;" /> ' % (value,)))
        output.append(super(SimpleImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


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
    label='Invite Sarcoma Central Members',
    help_text='Start typing or select member(s) in the list',
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
        widget=CKEditorWidget(),
        required=False,
        help_text="Custom message that will be added to the invitation email"
    )


static_invite_text = 'You are invited by [First Name, Last Name of \
moderator] to join the [Group Name] group in Sarcoma Central network.\
\n\nIf you’re not already a Rapid Science member, please register here. \
\n\nSincerely, \
\n\nThe Sarcoma Central Team \
\n\n@RapidScience'

GROUP_APPROVAL_CHOICES = (
    (0, ('Open - All validated Sarcoma Central members can '
         'view activity and join to participate')),
    (1, 'Closed - Moderator must approve / invite Sarcoma Central members'))


class BaseGroupForm(forms.Form):
    group_name = forms.CharField(max_length=200)
    about = forms.CharField(max_length=300, widget=forms.Textarea)
    banner_image = forms.ImageField(required=False)
    approval = forms.ChoiceField(
        widget=forms.RadioSelect, choices=GROUP_APPROVAL_CHOICES)


class NewGroupForm(BaseGroupForm):
    """ Adds invites to the ModifyGroupForm to create a new group.
        TODO: seems like it could mixin the InviteForm too
    """
    internal = internal_member_field
    external = external_member_field
    initial_text = static_invite_text
    invitation_message = forms.CharField(
        max_length=600,
        widget=forms.Textarea,
        required=False,
        help_text="Custom message that will be added to the invitation email",
    )

    field_order = ['group_name', 'about', 'banner_image', 'approval',
                   'internal', 'external']


class ModifyGroupForm(NewGroupForm):
    """ Hides the approval field and adds a hidden group id to the base form.
    """
    group_id = forms.IntegerField(widget=forms.HiddenInput())

    # friendlier image widget
    banner_image = forms.ImageField(required=False, widget=SimpleImageWidget())

    approval = forms.IntegerField(widget=forms.HiddenInput())
    # remember to ensure that approval doesn't change, and the the user is a moderator for the group
