from datetime import datetime, timedelta

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient
from tests.test_utils import BaseTestCase, User

from jwt_devices.models import Device
from jwt_devices.settings import api_settings


class ObtainJSONWebTokenTests(BaseTestCase):
    def test_jwt_permanent_token_auth(self):
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_MODEL="Nokia", HTTP_USER_AGENT="agent")
        self.assertEqual(Device.objects.all().count(), 0)
        response = client.post("/auth-token/", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"token", "permanent_token", "device_id"})
        device = Device.objects.get(permanent_token=response.data["permanent_token"])
        self.assertEqual(response.data["device_id"], device.id)
        self.assertIsNotNone(response.data["token"])
        self.assertEqual(device.name, "Nokia")
        self.assertEqual(device.details, "agent")
        self.assertEqual(Device.objects.all().count(), 1)
        Device.objects.all().delete()

        # test using without setting device model - for example on browser
        client.credentials(HTTP_USER_AGENT="agent")
        self.assertEqual(Device.objects.all().count(), 0)
        response = client.post("/auth-token/", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["token"]
        device = Device.objects.get(permanent_token=response.data["permanent_token"])
        self.assertEqual(response.data["device_id"], device.id)
        self.assertEqual(device.name, "agent")
        self.assertEqual(device.details, "")
        self.assertEqual(Device.objects.all().count(), 1)
        self.assertEqual(Device.objects.get(permanent_token=response.data["permanent_token"]).name, "agent")

        # check if the generated token works
        client.credentials(HTTP_AUTHORIZATION="JWT {}".format(token))
        client.login(**self.data)
        response = client.get("/devices/", format="json")
        self.assertEqual(response.status_code, 200)

        device.delete()
        # test login with unknown device
        client.credentials(HTTP_AUTHORIZATION="JWT {}".format(token))
        client.login(**self.data)
        response = client.get("/devices/", format="json")
        self.assertEqual(response.status_code, 404)

    def test_default_auth(self):
        # the app should allow using the old-style authentication
        api_settings.JWT_PERMANENT_TOKEN_AUTH = False
        client = APIClient()
        client.credentials(HTTP_X_DEVICE_MODEL="Nokia", HTTP_USER_AGENT="agent")
        self.assertEqual(Device.objects.all().count(), 0)
        response = client.post("/auth-token/", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"token"})
        self.assertIsNotNone(response.data["token"])
        self.assertEqual(Device.objects.all().count(), 0)
        token = response.data["token"]

        # check if the generated token works
        client.credentials(HTTP_AUTHORIZATION="JWT {}".format(token))
        client.login(**self.data)
        response = client.get("/devices/", format="json")
        self.assertEqual(response.status_code, 200)
        api_settings.JWT_PERMANENT_TOKEN_AUTH = True


class DeviceLogoutViewTests(BaseTestCase):
    def setUp(self):
        super(DeviceLogoutViewTests, self).setUp()
        self.second_user = User.objects.create_user(
            self.username + "2", self.email + "2", self.password)

    def test_logout_view(self):
        client = APIClient()

        # create device
        headers = {"HTTP_X_DEVICE_MODEL": "Android 123"}
        client.credentials(**headers)
        response = client.post("/auth-token/", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.all().count(), 1)
        device_id = response.data["device_id"]

        headers["HTTP_AUTHORIZATION"] = "JWT {}".format(response.data["token"])
        headers["HTTP_DEVICE_ID"] = device_id
        client.credentials(**headers)
        client.login(**self.data)
        response = client.delete("/device-logout/", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Device.objects.all().count(), 0)

    def test_logout_unknown_device(self):
        client = APIClient()

        # create a few devices
        headers = {"HTTP_X_DEVICE_MODEL": "Android 123"}
        client.credentials(**headers)
        response = client.post("/auth-token/", self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["token"]

        headers["HTTP_X_DEVICE_MODEL"] = "Nokia"
        client.credentials(**headers)
        response = client.post("/auth-token/", {"username": self.second_user.username, "password": self.password},
                               format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.all().count(), 2)
        device_id = response.data["device_id"]

        headers["HTTP_AUTHORIZATION"] = "JWT {}".format(token)
        headers["HTTP_DEVICE_ID"] = device_id
        client.credentials(**headers)
        client.login(**self.data)
        response = client.delete("/device-logout/", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Device.objects.all().count(), 2)


class DeviceRefreshTokenViewsTests(BaseTestCase):
    def setUp(self):
        super(DeviceRefreshTokenViewsTests, self).setUp()

    def test_refreshing(self):
        with freeze_time("2016-01-01 00:00:00") as frozen_time:
            client = APIClient()

            headers = {"HTTP_X_DEVICE_MODEL": "Android 123"}
            client.credentials(**headers)
            response = client.post("/auth-token/", self.data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            permanent_token = response.data["permanent_token"]
            old_token = response.data["token"]

            frozen_time.tick(delta=timedelta(days=2))
            # test w/o passing permanent_token
            response = client.post("/device-refresh-token/", format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            # test passing permanent token that does not exist in the database
            fake_permanent_token = "23124csfdgfdhthfdfdf"
            self.assertEqual(Device.objects.filter(permanent_token=fake_permanent_token).count(), 0)
            headers["HTTP_PERMANENT_TOKEN"] = fake_permanent_token
            client.credentials(**headers)
            response = client.post("/device-refresh-token/", format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            headers["HTTP_PERMANENT_TOKEN"] = permanent_token
            client.credentials(**headers)
            response = client.post("/device-refresh-token/", format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(set(response.data.keys()), {"token"})
            device = Device.objects.get(permanent_token=permanent_token)
            self.assertEqual(device.last_request_datetime, datetime.now())
            token = response.data["token"]
            self.assertNotEqual(token, old_token)

            # test auth with the new token
            client.credentials(HTTP_AUTHORIZATION="JWT {}".format(token))
            client.login(**self.data)
            response = client.get("/devices/")
            self.assertEqual(response.status_code, 200)

            # test permanent token expiration
            frozen_time.tick(delta=timedelta(days=8))
            client.credentials(**headers)
            response = client.post("/device-refresh-token/", format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            with self.assertRaises(Device.DoesNotExist):
                Device.objects.get(permanent_token=permanent_token)


class DeviceViewTests(BaseTestCase):
    def setUp(self):
        super(DeviceViewTests, self).setUp()
        self.device = Device.objects.create(
            user=self.user, permanent_token="somestring2", name="Android",
            last_request_datetime=datetime.now())
        self.user2 = User.objects.create_user(email="jsmith@example.com", username="jsmith", password="password")
        self.device2 = Device.objects.create(
            user=self.user2, permanent_token="somestring98", name="Android",
            last_request_datetime=datetime.now())

    def _get_token(self):
        client = APIClient()
        response = client.post("/auth-token/", self.data, format="json")
        return response.data["token"]

    def _login(self, client):
        client.credentials(HTTP_AUTHORIZATION="JWT {}".format(self._get_token()))
        return client.login(**self.data)

    def test_device_delete(self):
        client = APIClient()
        # test accessing without being logged in
        response = client.delete("/devices/{}/".format(self.device.id))
        self.assertEqual(response.status_code, 401)

        self._login(client)
        # try removing device linked to other user
        response = client.delete("/devices/{}/".format(self.device2.id))
        self.assertEqual(response.status_code, 404)
        # test regular case
        self.assertEqual(Device.objects.filter(id=self.device.id).count(), 1)
        response = client.delete("/devices/{}/".format(self.device.id))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Device.objects.filter(id=self.device.id).count(), 0)

    def test_device_list(self):
        client = APIClient()
        self._login(client)
        response = client.get("/devices/", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # one created in setUp() and one during _login()
        self.assertEqual(set(response.data[0].keys()), {
            "id", "created", "name", "details", "last_request_datetime"
        })
        self.assertEqual(response.data[0]["id"], self.device.id)
