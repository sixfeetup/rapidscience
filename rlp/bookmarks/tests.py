import unittest
import json
from django.test import TestCase
from django.test import Client
from rlp.accounts.models import User
from rlp.bookmarks.models import Bookmark
from rlp import settings


class BookmarkTest(TestCase):
    def setUp(self):
        settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
        self.user = User.objects.create_user(
            email='jacob@gmail.com', password='top_secret')

        self.bookmark = Bookmark(
            name='Bookmark #1',
            content_type_id=1,
            owner=self.user
        )
        self.bookmark.save()

    @staticmethod
    def get_data_response(response):
        data_decode = response.content.decode(response.charset)
        data_object = json.loads(data_decode)
        return data_object

    def test_bookmark_update(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'jacob@gmail.com', 'password': 'top_secret'})

        update_url = '/bookmarks/{0}/update/'.format(self.bookmark.id)
        response = c.post(update_url, {'name': 'Bookmark New'})
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], False)

        update_url = '/bookmarks/{0}/update/'.format(999)
        response = c.post(update_url, {'name': 'Bookmark F'})
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], True)

    def test_bookmark_delete(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'jacob@gmail.com', 'password': 'top_secret'})

        delete_url = '/bookmarks/{0}/delete/'.format(self.bookmark.id)
        response = c.post(delete_url)
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], False)

    def test_add_bookmark_folder(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'jacob@gmail.com', 'password': 'top_secret'})

        response = c.post('/bookmarks/folders/add/', {'name': 'Folder #1'})
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], False)
        self.assertEqual(isinstance(data['folder_id'], int), True)
        self.assertEqual(data['folder_name'], 'Folder #1')

        response = c.post('/bookmarks/folders/add/', {'name': 'Folder #1'})
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], True)

    def test_delete_bookmark_folder(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'jacob@gmail.com', 'password': 'top_secret'})

        response = c.post('/bookmarks/folders/add/', {'name': 'Folder #1'})
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        folder_id = data['folder_id']

        response = c.post('/bookmarks/folders/{0}/delete/'.format(folder_id))
        self.assertEqual(response.status_code, 200)
        data = self.get_data_response(response)
        self.assertEqual(data['error'], False)

if __name__ == '__main__':
    unittest.main()
