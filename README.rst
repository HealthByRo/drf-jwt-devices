===============
drf-jwt-devices
===============
|travis|_ |pypi|_ |coveralls|_ |requiresio|_

Permanent token feature for `Django Rest Framework JWT <https://github.com/GetBlimp/django-rest-framework-jwt>`_

By default JWT tokens have short lifetime because of security reasons, but sometimes you may want to keep user logged
in, without the need to refresh the auth token each 5 minutes. For this case, you should consider using the permanent
token authentication.

Installation
============
To use, add ``jwt_devices`` to your ``INSTALLED_APPS``, and then migrate the project.

Configuration
-------------

To enable permanent token authentication, update rest framework's default authentication classes list:
::

    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "jwt_devices.authentication.PermanentTokenAuthentication"
        ]
    }

Another step is to add a few urls to your url patterns, and register the ``DeviceViewSet``:
::

  from jwt_devices import views
  from rest_framework.routers import DefaultRouter

  router = DefaultRouter()
  router.register(r'devices', views.DeviceViewSet)
  
  urlpatterns = [
      # ...
      url(r'^device-refresh-token/$', views.device_refresh_token),
      url(r'^device-logout/$', views.device_logout)
  ] + router.urls


Using the API views
-------------------

**Login & logout view**

When using the regular JWT login or the device logout view, use the ``HTTP_X_DEVICE_MODEL`` header to pass device model
(otherwise, user agent will used instead as the name). After a successful login, the permanent token and id of the
created device will be returned, for example:
::

  {
      "token": "ads344fdgfd5454yJ0eAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VynRlYW1AYXJhYmVsLmxh",
      "permanent_token": "gfd5454yJ0eAiOiJKV1QiLCJhbGciOiJ",
      "device_id": 1
  }

The ``device_id`` is used to logout the device, so it should be saved on the front-end side (in local storage, for
example).

To logout a device, make a **DELETE** request to the ``rest_framework_jwt.views.device_logout`` view, passing device's
id in the ``device_id`` header to identify the device.

**Refresh JWT token using permanent token**

To refresh JWT token, you have to pass the ``permanent_token`` header along with the request to identify the device.
On success, response will return new JWT token (the same as it does after login).

In case the permanent token has expired, the device will be logged out, and it will require login in again to obtain a
new permanent token. To customize the expiration time and expiration accuracy, set the following settings in your
``REST_FRAMEWORK`` configuration in **settings.py**


**PermitHeaders middleware**

As you may know, the content of a permanent token is a very fragile information, which should be sent along with a
request only when it is needed. To avoid situations in which a front-end developer has incorrectly implemented the
permanent token authentication on the front-end side and the permanent token value is sent with all requests
(just like the JWT token), the ``jwt_devices.middleware.PermitHeadersMiddleware`` comes in handy. The middleware looks
for the ``permanent_token`` in the headers, and checks if the view is not the
``jwt_devices.views.DeviceRefreshJSONWebToken`` in which the ``permanent_token`` header is obligatory, otherwise it
returns a **400 Bad Request** error.

To use the ``PermitHeadersMiddleware`` in your application, add ``jwt_devices.middleware.PermitHeadersMiddleware``
to your ``MIDDLEWARES`` or ``MIDDLEWARE_CLASSES`` (in Django <1.10) in Django settings.

**Settings**

* ``JWT_PERMANENT_TOKEN_AUTH`` - option to enable/disable the permanent token authentication (default: ``True``)
* ``JWT_PERMANENT_TOKEN_EXPIRATION_DELTA`` - describes how long can the permanent token live
  (default: ``datetime.timedelta(days=7)``)
* ``JWT_PERMANENT_TOKEN_EXPIRATION_ACCURACY`` - the accuracy of updating permanent token last request time to decrease
  the number of database queries (default: ``datetime.timedelta(minutes=30)``)

Support
=======
* Django 1.8 - 1.11
* Django Rest Framework 3.1 - 3.5
* Python 2.7, 3.4, 3.5, 3.6

.. |travis| image:: https://secure.travis-ci.org/ArabellaTech/drf-jwt-devices.svg?branch=master
.. _travis: http://travis-ci.org/ArabellaTech/drf-jwt-devices

.. |pypi| image:: https://img.shields.io/pypi/v/drf-jwt-devices.svg
.. _pypi: https://pypi.python.org/pypi/drf-jwt-devices

.. |coveralls| image:: https://coveralls.io/repos/github/ArabellaTech/drf-jwt-devices/badge.svg?branch=master
.. _coveralls: https://coveralls.io/github/ArabellaTech/drf-jwt-devices

.. |requiresio| image:: https://requires.io/github/ArabellaTech/drf-jwt-devices/requirements.svg?branch=master
.. _requiresio: https://requires.io/github/ArabellaTech/drf-jwt-devices/requirements/
