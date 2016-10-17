from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver

from rlp.accounts.models import User
from rlp.projects.models import Project


class ProjectTestCase(StaticLiveServerTestCase):
    fixtures = [
        'accounts.json',
        'projects.json',
        'cms.json',
        'documents.json',
        'bibliography.json',
        'discussions.json',
        'activity_stream.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.project = Project.objects.first()
        self.project_approval_required = Project.objects.get(pk=1)
        self.member_of_approval_required = User.objects.get(pk=2)
        self.project_approval_not_required = Project.objects.get(pk=7)
        self.member_of_approval_not_required = User.objects.get(pk=3)
        # Sanity checks
        # Make sure that we have projects with institutions
        assert Project.objects.filter(institution__isnull=False).count()
        # Make sure we have at least one project with documents and references to show
        assert self.project.document_set.count()
        assert self.project.projectreference_set.count()
        # Make sure we have at least one project that is the target of activity stream items
        assert self.project.target_actions.count()

    def test_anonymous_on_project_detail(self):
        """Tests that if a user is not logged in that they can only see the public details of a project (goal, biblio)
        but not any other activity.
        """
        driver = self.driver
        driver.get(self.live_server_url)
        # Click the 'Projects' main nav item
        driver.find_element_by_id("nav-6").click()
        projects_with_institutions = Project.objects.filter(institution__isnull=False)
        # Make sure we have projects with institutions set
        assert projects_with_institutions.count()
        # Make sure these projects appear on the list page
        for project in projects_with_institutions:
            self.assertIn(project.title, driver.page_source)
            self.assertIn('({})'.format(project.institution.name), driver.page_source)
        # Go to a project detail page
        driver.find_element_by_link_text(self.project.title).click()
        self.assertEqual(
            driver.current_url,
            '{}{}'.format(self.live_server_url, self.project.get_absolute_url())
        )
        assert self.project.projectreference_set.count()
        for pr in self.project.projectreference_set.all():
            self.assertIn(pr.reference.title, driver.page_source)
        assert self.project.document_set.count()
        # Make sure no docs are shown
        for doc in self.project.document_set.all():
            self.assertNotIn(doc.title, driver.page_source)

    def test_member_of_approval_not_required(self):
        """Tests that if a member belongs to a project that does NOT require approval to join, that they are not able to
         view details for projects that DO require approval to join.
        """
        driver = self.driver
        driver.get(self.live_server_url)
        driver.find_element_by_link_text("Sign in").click()
        driver.find_element_by_id("id_username").send_keys(self.member_of_approval_not_required.email)
        driver.find_element_by_id("id_password").send_keys("password")
        driver.find_element_by_css_selector(".plugin-form button.btn.btn-primary").click()
        self.assertEqual('{}{}'.format(self.live_server_url, reverse('dashboard')), driver.current_url)
        # Make sure they only see activity for projects that don't require approval on their dashboard
        for project in Project.objects.all():
            # If there isn't any activity for this project, there is nothing to test
            if not project.target_actions.count():
                continue
            try:
                driver.find_element_by_css_selector(
                    '.activity-stream .small a[href="{}"]'.format(project.get_absolute_url()))
            except NoSuchElementException:
                # We should not get an exception for projects that don't require approval
                if not project.approval_required:
                    assert False
            else:
                # An exception should have been raised if this project requires approval
                if project.approval_required:
                    assert False
        # Click the 'Projects' main nav item
        driver.find_element_by_id("nav-6").click()
        # Make sure these projects appear on the list page
        for project in Project.objects.all():
            self.assertIn(project.title, driver.page_source)
            if project.institution:
                self.assertIn('({})'.format(project.institution.name), driver.page_source)
            # Go to the project detail page
            driver.find_element_by_link_text(project.title).click()
            self.assertEqual(
                driver.current_url,
                '{}{}'.format(self.live_server_url, project.get_absolute_url())
            )
            for pr in project.projectreference_set.all():
                self.assertIn(pr.reference.title, driver.page_source)
            # Make sure docs are shown in the activity stream only if they have permission
            for doc in project.document_set.all():
                if project.approval_required:
                    self.assertNotIn(doc.get_absolute_url(), driver.page_source)
                else:
                    self.assertIn(doc.get_absolute_url(), driver.page_source)
            # Go back to the project list page to reset `drive.page_source`
            driver.find_element_by_id("nav-6").click()

    def test_member_of_approval_required(self):
        """Tests that if a member belongs to a project that requires approval to join, that they are able to view all
        details for all projects.
        """
        driver = self.driver
        driver.get(self.live_server_url)
        driver.find_element_by_link_text("Sign in").click()
        driver.find_element_by_id("id_username").send_keys(self.member_of_approval_required.email)
        driver.find_element_by_id("id_password").send_keys("password")
        driver.find_element_by_css_selector(".plugin-form button.btn.btn-primary").click()
        self.assertEqual('{}{}'.format(self.live_server_url, reverse('dashboard')), driver.current_url)
        # Make sure they see all activity on their dashboard
        for project in Project.objects.all():
            # If there isn't any activity for this project, there is nothing to test
            if not project.target_actions.count():
                continue
            try:
                driver.find_element_by_css_selector(
                    '.activity-stream .small a[href="{}"]'.format(project.get_absolute_url()))
            except NoSuchElementException:
                # We should not have any exceptions
                assert False
            else:
                assert True
        # Click the 'Projects' main nav item
        driver.find_element_by_id("nav-6").click()
        # Make sure these projects appear on the list page
        for project in Project.objects.all():
            self.assertIn(project.title, driver.page_source)
            if project.institution:
                self.assertIn('({})'.format(project.institution.name), driver.page_source)
            # Go to the project detail page
            driver.find_element_by_link_text(project.title).click()
            self.assertEqual(
                driver.current_url,
                '{}{}'.format(self.live_server_url, project.get_absolute_url())
            )
            for pr in project.projectreference_set.all():
                self.assertIn(pr.reference.title, driver.page_source)
            # Make sure docs are shown in the activity stream
            for doc in project.document_set.all():
                self.assertIn(doc.get_absolute_url(), driver.page_source)
            # Go back to the project list page to reset `drive.page_source`
            driver.find_element_by_id("nav-6").click()
