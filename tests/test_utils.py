from django.test import TestCase
from rest_framework_jwt.compat import get_user_model

from jwt_devices.settings import api_settings

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.email = "jpueblo@example.com"
        self.username = "jpueblo"
        self.password = "password"
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.data = {
            "username": self.username,
            "password": self.password
        }

        api_settings.JWT_PERMANENT_TOKEN_AUTH = True

    def tearDown(self):
        api_settings.JWT_PERMANENT_TOKEN_AUTH = False
