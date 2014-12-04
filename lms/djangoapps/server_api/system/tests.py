# pylint: disable=E1103

"""
Run these tests @ Devstack:
    paver test_system -s lms --fasttest --verbose --test_id=lms/djangoapps/server_api
"""
import uuid

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.test.utils import override_settings

TEST_API_KEY = str(uuid.uuid4())


class SecureClient(Client):
    """ Django test client using a "secure" connection. """
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs.update({'SERVER_PORT': 443, 'wsgi.url_scheme': 'https'})
        super(SecureClient, self).__init__(*args, **kwargs)


@override_settings(EDX_API_KEY=TEST_API_KEY)
class SystemApiTests(TestCase):
    """ Test suite for base API views """

    def setUp(self):
        self.client = SecureClient()

    def do_get(self, uri):
        """Submit an HTTP GET request"""
        headers = {
            'Content-Type': 'application/json',
            'X-Edx-Api-Key': str(TEST_API_KEY),
        }
        response = self.client.get(uri, headers=headers)
        return response

    def build_url(self, path):
        """
        Build test server URL.
        :param path: Path for URL
        """
        return "https://testserver{}".format(path)

    def test_system_detail_get(self):
        """ Ensure the system returns base data about the system """
        test_uri = self.build_url(reverse('server_api:system'))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)
        self.assertIsNotNone(response.data['description'])
        self.assertGreater(len(response.data['description']), 0)

    def test_system_detail_api_get(self):
        """ Ensure the system returns base data about the API """
        test_uri = self.build_url(reverse('server_api:root'))
        response = self.do_get(test_uri)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['uri'])
        self.assertGreater(len(response.data['uri']), 0)
        self.assertEqual(response.data['uri'], test_uri)
        self.assertGreater(len(response.data['csrf_token']), 0)
        self.assertIsNotNone(response.data['name'])
        self.assertGreater(len(response.data['name']), 0)
        self.assertIsNotNone(response.data['description'])
        self.assertGreater(len(response.data['description']), 0)
        self.assertIsNotNone(response.data['resources'])
