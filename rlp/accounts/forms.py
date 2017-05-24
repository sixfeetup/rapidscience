from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm as DJAuthForm, \
    PasswordResetForm as DJPasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from .models import User, Institution
from rlp.core.email import send_transactional_mail
from rlp.projects.models import Project, ProjectMembership

PASSWORD_RESET_SUBJECT = "Reset your password"


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.

    Used in django admin and to inherit off of enduser-facing forms.
    """

    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'email_mismatch': _("The two email fields didn't match."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get("email").lower().strip()
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_email_confirmation(self):
        """
        Only used for the following child form:
            + UserRegistrationForm
        """
        email1 = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email_confirmation').lower().strip()

        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        validate_password(password2)
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AuthenticationForm(DJAuthForm):
    """Overrides the default implementation to use an EmailField instead of CharField and ensures that the email
    address is lower-cased before authenticating.
    The error message is also customized to only indicate that the password is case-sensitive.
    """
    username = forms.EmailField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that passwords are case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def clean_username(self):
        # Clean up the email address so we get consistent results regardless of what casing the user types their
        # email address
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
        return username


class RegistrationForm(UserCreationForm):
    email_confirmation = forms.EmailField(max_length=254)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    institution = forms.ModelChoiceField(
        label="Primary Institution",
        queryset=Institution.objects.all(),
        required=False)
    new_institution = forms.BooleanField(
        label="My institution is not listed",
        required=False)
    institution_name = forms.CharField(max_length=80, required=False)
    institution_city = forms.CharField(max_length=80, required=False)
    institution_state = forms.CharField(max_length=80, required=False)
    institution_country = forms.CharField(max_length=80, required=False)
    institution_website = forms.CharField(max_length=80, required=False)
    title = forms.CharField(label="Position", max_length=80, required=False)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    field_order = ['first_name', 'last_name', 'institution', 'new_institution',
                   'institution_name', 'institution_city', 'institution_state',
                   'institution_country', 'institution_website', 'title',
                   'email', 'email_confirmation', 'password1', 'password2']
    honeypot = forms.CharField(
        label="If you are human, leave this field blank",
        max_length=30, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'institution', 'title',
                  'email', 'email_confirmation']

    def email_domain_matches(self):
        if not self.cleaned_data:
            return
        email = self.cleaned_data.get('email')
        institution = self.cleaned_data.get('institution')
        if not institution:
            return False
        domains = tuple(institution.institutiondomain_set.values_list('domain', flat=True))
        return email.endswith(domains)


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class ProjectMembershipForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset=Project.objects.exclude(auto_opt_in=True))
    class Meta:
        exclude = ['user']
        model = ProjectMembership


class RestrictedProjectMembershipForm(ProjectMembershipForm):
    project = forms.ModelChoiceField(queryset=Project.objects.exclude(auto_opt_in=True).filter(approval_required=False))


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    title = forms.CharField(max_length=255, required=True, label='Position')

    class Meta:
        model = User
        fields = [
            'photo', 'banner', 'first_name', 'last_name', 'degrees', 'title',
            'department', 'institution', 'email', 'website',
            'orcid', 'linkedin', 'twitter', 'bio', 'research_interests',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'remaining-characters'}),
            'research_interests': forms.TextInput(attrs={'class': 'remaining-characters'})
        }

    def clean_email(self):
        return self.cleaned_data.get("email").lower()


class PasswordResetForm(DJPasswordResetForm):
    error_messages = {
        'non_existing_user': "The email address you've entered does not have "
                             "an associated user account. "
                             "Please re-enter a valid email address."
    }

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages['non_existing_user'],
                code='non_existing_user')

        return email

    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            context = {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            }
            subject = PASSWORD_RESET_SUBJECT
            send_transactional_mail(user.email, subject, 'emails/password_reset', context)
