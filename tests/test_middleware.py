from rest_framework import status
from rest_framework.test import APIClient
from tests.test_utils import BaseTestCase


class HeadersCheckViewMixinTests(BaseTestCase):
    def test_disallowing_permanent_token(self):
        client = APIClient()
        client.credentials(HTTP_PERMANENT_TOKEN="123")
        urls = {
            "/auth-token/",
            "/device-logout/",
            "/devices/",
            "/devices/1/"
        }
        for url in urls:
            # request method makes no difference here, as the check is done in middleware
            response = client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        allowed_urls = [
            "/device-refresh-token/"
        ]
        for url in allowed_urls:
            response = client.get(url, format="json")
            self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
