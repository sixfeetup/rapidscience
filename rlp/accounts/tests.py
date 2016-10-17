from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import User, Institution
from .views import Register, PENDING_REGISTRATION_MESSAGE
from rlp.projects.models import Project, ProjectMembership, Role


class UserTest(TestCase):
    fixtures = ['projects.json', 'cms.json', 'accounts.json']

    def setUp(self):
        self.user = User.objects.get(last_name='User')
        self.project_approval_not_required = Project.objects.filter(approval_required=False).first()
        self.project_approval_required = Project.objects.filter(approval_required=True).first()
        self.auto_optin_projects = Project.objects.filter(auto_opt_in=True)
        assert self.auto_optin_projects
        self.contact_role = Role.objects.filter(contact=True).first()
        self.institution = Institution.objects.first()
        self.register_url = reverse('register')
        self.dashboard_url = reverse('dashboard')

        self.registration_data = {
            'register-current_step': 'register',
            'register-first_name': 'Test',
            'register-last_name': 'User2',
            'register-email': 'test-user2@example.com',
            'register-email_confirmation': 'test-user2@example.com',
            'register-password1': 'password',
            'register-password2': 'password',
            'register-institution': str(self.institution.id),
            'register-project': str(self.project_approval_required.id),
            'register-role': '9',
        }

    def test_cant_register_as_contact_role(self):
        response = self.client.get(self.register_url)
        self.assertNotContains(response, self.contact_role.title)
        registration_data = self.registration_data.copy()
        registration_data.update({
            'register-role': str(self.contact_role.id),
        })
        response = self.client.post(self.register_url, registration_data, follow=True)
        self.assertFormError(
            response, 'form', 'role', 'Select a valid choice. That choice is not one of the available choices.')

    def test_register_for_project_approval_required(self):
        """Tests that if the user selects a project where approval is required, that this triggers the approval process.
        They should not be allowed to login until they have been approved.
        """
        self.client.get(self.register_url)
        response = self.client.post(self.register_url, self.registration_data, follow=True)
        # Test that the user is redirected to the home page with the appropriate messaging and that they cannot login
        self.assertRedirects(response, '/')
        self.assertContains(response, PENDING_REGISTRATION_MESSAGE.format(settings.SITE_PREFIX.upper()))
        user = User.objects.get(email=self.registration_data['register-email'])
        self.assertEqual(user.is_active, False)
        # Test that the notification email was sent to the appropriate contacts
        self.assertEqual(set(mail.outbox[0].recipients()), set(self.project_approval_required.get_contact_email_addresses()))
        self.assertIn(self.project_approval_required.title, mail.outbox[0].body)
        # Test that the email contains the activation key
        # The full activation key is NOT identical to the one originally sent to the recipients since it contains
        # salt/timestamp information e.g. 'InRlc3QtdXNlcjJAZXhhbXBsZS5jb20i:1ahsLK:DuDbt8t4-2P0uyBbacln-uXsbg8'
        # We only check the first part which contains the user's email address.
        activation_key = Register().get_activation_key(user)
        self.assertEqual(mail.outbox[0].body.count(activation_key.split(':')[0]), 1)
        # Clear the mailbox
        mail.outbox = []
        # Test that if the activation link is followed, that the user is activated
        # NOTE: we're using a newly constructed url and NOT the one included in the email.
        # Too lazy to use to pluck it out of the email using regex's etc.
        response = self.client.get(reverse('registration_activate', kwargs={'activation_key': activation_key}),
                                   follow=True)
        self.assertRedirects(response, '/')
        self.assertContains(response, "{} is now approved to complete their registration.".format(user.email))
        # Test that the user is now active
        user = User.objects.get(email=self.registration_data['register-email'])
        self.assertEqual(user.is_active, True)
        # Test that the user receives the welcome email
        self.assertEqual(mail.outbox[0].recipients(), [user.email])
        self.assertIn(user.get_full_name(), mail.outbox[0].body)
        self.assertIn('Your registration has been approved', mail.outbox[0].body)
        self.assertIn(reverse('profile_edit'), mail.outbox[0].body)
        # Test that the user was automatically added to auto opt-in projects
        for project in self.auto_optin_projects:
            ProjectMembership.objects.get(user=user, project=project)
        # Test that the user can now log in
        response = self.client.get(reverse('profile_edit'))
        redirect_url = "{}?next={}".format(reverse('login'), reverse('profile_edit'))
        self.assertRedirects(response, redirect_url)
        response = self.client.post(redirect_url, data={'username': user.email, 'password': 'password'},
                                    follow=True)
        # Test that the user is redirected to their edit profile page
        self.assertRedirects(response, reverse('profile_edit'))

    def test_register_for_project_if_email_domain_validates(self):
        """Tests that if the user selects a project where approval is *not* officially required, that they can
        register for the project if their email address domain matches their institution."""
        registration_data = self.registration_data.copy()
        domain = self.institution.institutiondomain_set.first().domain
        # Note that we add a subdomain to test that we all any subdomain through, we only check if it endswith domain
        email = 'test-user2@subdomain.{}'.format(domain)
        registration_data.update({
            'register-email': email,
            'register-email_confirmation': email,
            'register-project': str(self.project_approval_not_required.id)
        })
        self.client.get(self.register_url)
        response = self.client.post(self.register_url, registration_data, follow=True)
        self.assertIn('You are now registered', mail.outbox[0].body)
        user = User.objects.get(email=email)
        # Test that the user was automatically added to auto opt-in projects
        for project in self.auto_optin_projects:
            ProjectMembership.objects.get(user=user, project=project)
        self.assertRedirects(response, self.dashboard_url)

    def test_approval_required_if_email_validation_fails(self):
        """Tests that if the user selects a project where approval is *not* officially required BUT their email address
        does *not* match their chosen institution, that this triggers the approval process."""
        registration_data = self.registration_data.copy()
        registration_data.update({
            'register-email': 'test-user2@not-at-all-valid.com',
            'register-email_confirmation': 'test-user2@not-at-all-valid.com',
            'register-project': str(self.project_approval_not_required.id)
        })
        self.client.get(self.register_url)
        response = self.client.post(self.register_url, registration_data, follow=True)
        # Test that the user is redirected to the home page with the appropriate messaging and that they cannot login
        self.assertRedirects(response, '/')
        self.assertContains(response, PENDING_REGISTRATION_MESSAGE.format(settings.SITE_PREFIX.upper()))
        user = User.objects.get(email=registration_data['register-email'])
        self.assertEqual(user.is_active, False)

    def test_case_insensitive_email(self):
        # We should always normalize email to lowercase, this tests that logging in works
        # even if the user mixes the casing of their email
        login_data = {
            'username': self.user.email.upper(),
            'password': 'password'
        }
        response = self.client.post(reverse('login'), login_data, follow=True)
        # If a user logs in directly from the login page without visiting a previous page, they should be
        # redirected to their dashboard
        self.assertRedirects(response, self.dashboard_url)
