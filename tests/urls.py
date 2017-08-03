from django.conf.urls import url
from rest_framework import routers

from jwt_devices import views

router = routers.SimpleRouter()
router.register(r"devices", views.DeviceViewSet)

urlpatterns = [
    url(r"^auth-token/$", views.obtain_jwt_token),
    url(r"^device-refresh-token/$", views.device_refresh_token),
    url(r"^device-logout/$", views.device_logout),
] + router.urls
