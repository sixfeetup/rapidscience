import time

from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver

from rlp.accounts.models import User


class DiscussionTestCase(StaticLiveServerTestCase):
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
        self.member = User.objects.get(pk=2)
        self.project = self.member.projects.first()
        # Login
        self.driver.get('{}{}'.format(self.live_server_url, reverse('login')))
        self.driver.find_element_by_id('id_username').send_keys(self.member.email)
        self.driver.find_element_by_id('id_password').send_keys('password')
        self.driver.find_element_by_css_selector('.plugin-form button.btn.btn-primary').click()

    def test_create_comment_thread(self):
        """Tests that a logged-in member can create a comment thread on one of their projects.
        """
        # Go to the project discussion tab
        self.driver.get('{}{}'.format(self.live_server_url, self.project.get_discussions_url()))
        # Start 5 new topics
        for i in range(5):
            self.driver.find_element_by_css_selector('button[href="#topic-form"]').click()
            time.sleep(1)
            self.driver.find_element_by_id('id_title').send_keys('{} title'.format(i))
            self.driver.find_element_by_id('id_comment').send_keys('{} comment'.format(i))
            self.driver.find_element_by_css_selector(".plugin-form button.btn.btn-primary").click()
            time.sleep(0.5)
        comments = self.member.comment_comments.filter(object_pk=str(self.project.id))
        assert comments.count()
        # Test that the comments show up correctly in the discussions page
        self.driver.get('{}{}'.format(self.live_server_url, self.project.get_discussions_url()))
        for comment in comments:
            self.assertIn(comment.threadedcomment.title, self.driver.page_source)
            self.assertIn(comment.comment, self.driver.page_source)
            self.assertIn(comment.threadedcomment.get_absolute_url(), self.driver.page_source)
        # Test the project activity stream
        self.driver.get('{}{}'.format(self.live_server_url, self.project.get_absolute_url()))
        for comment in comments:
            self.assertIn(comment.threadedcomment.get_absolute_url(), self.driver.page_source)

    def test_cant_create_duplicates(self):
        """Tests that duplicate comments are not allowed (this is enforced by django-contrib-comments) and that we don't
        accidentally make duplicate activity stream entries.
        """
        # Clear out any existing comments
        self.member.comment_comments.all().delete()
        # Go to the project discussion tab
        self.driver.get('{}{}'.format(self.live_server_url, self.project.get_discussions_url()))
        # Start 5 new topics
        for i in range(5):
            self.driver.find_element_by_css_selector('button[href="#topic-form"]').click()
            time.sleep(1)
            self.driver.find_element_by_id('id_title').send_keys('duplicate title')
            self.driver.find_element_by_id('id_comment').send_keys('duplicate comment')
            self.driver.find_element_by_css_selector(".plugin-form button.btn.btn-primary").click()
            time.sleep(0.5)
        comments = self.member.comment_comments.filter(object_pk=str(self.project.id))
        # Make sure we only made one comment
        self.assertEqual(comments.count(), 1)
        comment = comments.first()
        # Make sure we only have one entry on the activity stream
        self.driver.get('{}{}'.format(self.live_server_url, self.project.get_absolute_url()))
        self.assertEqual(self.driver.page_source.count(comment.threadedcomment.title), 1)
        self.assertEqual(comment.threadedcomment.action_object_actions.count(), 1)

