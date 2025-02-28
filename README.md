> **:warning: This fork is not currently maintained and will be archived then removed in the future.**

# drf-jwt-devices

[![PyPI version](https://img.shields.io/pypi/v/drf-jwt-devices.svg)](https://pypi.python.org/pypi/drf-jwt-devices)

Permanent token feature for [Django Rest Framework JWT](https://github.com/GetBlimp/django-rest-framework-jwt)

By default JWT tokens have short lifetime because of security reasons, but sometimes you may want to keep a user logged
in without the need to refresh the auth token every few minutes. For this case, you should consider using permanent
token authentication.

## Installation

To use, add `jwt_devices` to your `INSTALLED_APPS`, and then migrate the project.

## Configuration

To enable permanent token authentication, update Django REST framework's default authentication classes list:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "jwt_devices.authentication.PermanentTokenAuthentication"
    ]
}
```

Next, add a few URLs to your URL patterns, and register the `DeviceViewSet`:

```python
from jwt_devices import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)

urlpatterns = [
    # ...
    url(r'^device-refresh-token/$', views.device_refresh_token),
    url(r'^device-logout/$', views.device_logout),
] + router.urls
```

## Using the API views

### Login & logout view

When using the regular JWT login or the device logout view, use the `X-Device-Model` header to pass the device model
(otherwise, the user agent will be used as the name). After a successful login, the permanent token and the ID of the
created device will be returned, for example:

```json
{
  "token": "ads344fdgfd5454yJ0eAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VynRlYW1AYXJhYmVsLmxh",
  "permanent_token": "gfd5454yJ0eAiOiJKV1QiLCJhbGciOiJ",
  "device_id": 1
}
```

The `device_id` is used to log out the device, so it should be saved on the front-end side (e.g., in local storage).

To log out a device, make a **DELETE** request to `rest_framework_jwt.views.device_logout`, passing the device's ID
in the `Device-Id` header to identify the device.

### Refresh JWT token using permanent token

To refresh the JWT token, pass the `Permanent-Token` header along with the request to identify the device.
On success, the response will return a new JWT token (the same as it does after login).

If the permanent token has expired, the device will be logged out, and you will need to log in again to obtain a
new permanent token. To customize the expiration time and expiration accuracy, set the following settings in your
`REST_FRAMEWORK` configuration in **settings.py**.

### PermittedHeadersMiddleware

Because the content of a permanent token is very sensitive, it should only be sent when necessary. To avoid
accidentally sending the permanent token with every request, the `jwt_devices.middleware.PermittedHeadersMiddleware`
can be used. This middleware checks for the `Permanent-Token` header and ensures it is only sent to the
`jwt_devices.views.DeviceRefreshJSONWebToken` view. Otherwise, it returns a **400 Bad Request**.

To use `jwt_devices.middleware.PermittedHeadersMiddleware` in your application, add
`jwt_devices.middleware.jwt_devices.middleware.PermittedHeadersMiddleware` to your `MIDDLEWARE` (or
`MIDDLEWARE_CLASSES` if you're on Django <1.10) in the Django settings.

### Settings

- `JWT_PERMANENT_TOKEN_AUTH` – enable/disable permanent token authentication (default: `True`)
- `JWT_PERMANENT_TOKEN_EXPIRATION_DELTA` – how long the permanent token remains valid  
  (default: `datetime.timedelta(days=7)`)
- `JWT_PERMANENT_TOKEN_EXPIRATION_ACCURACY` – the accuracy of updating the permanent token’s last request time to
  reduce database queries (default: `datetime.timedelta(minutes=30)`)

## Support

- Django 1.8 - 1.11
- Django Rest Framework 3.1 - 3.8
- Python 3.4 - 3.6
