# from django.conf.urls import url
from rest_framework import routers

router = routers.SimpleRouter()
# TODO
# router.register(r'devices', views.DeviceViewSet)

urlpatterns = [
    # TODO
    # url(r'^device-refresh-token/$', views.device_refresh_token),
    # url(r'^device-logout/$', views.device_logout),
] + router.urls
