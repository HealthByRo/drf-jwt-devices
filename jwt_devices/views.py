from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import DestroyAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings as rfj_settings
from rest_framework_jwt.views import ObtainJSONWebToken as OriginalObtainJSONWebToken

from jwt_devices.models import Device
from jwt_devices.serializers import DeviceSerializer, DeviceTokenRefreshSerializer, JSONWebTokenSerializer
from jwt_devices.settings import api_settings

jwt_response_payload_handler = rfj_settings.JWT_RESPONSE_PAYLOAD_HANDLER
jwt_devices_response_payload_handler = api_settings.JWT_DEVICES_RESPONSE_PAYLOAD_HANDLER


class ObtainJSONWebTokenAPIView(OriginalObtainJSONWebToken):
    """Obtain JWT token
    API view used to obtain a JWT token along with creating a new Device object and returning permanent token.
    """
    serializer_class = JSONWebTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get("user") or request.user
            token = serializer.object.get("token")
            device = serializer.object.get("device", None)
            kwargs = {}
            if device:
                kwargs.update(dict(permanent_token=device.permanent_token, device_id=device.id))

            if api_settings.JWT_PERMANENT_TOKEN_AUTH:
                response_data = jwt_devices_response_payload_handler(token, user, request, **kwargs)
            else:
                response_data = jwt_response_payload_handler(token, user, request)

            response = Response(response_data)
            if rfj_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() + rfj_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(rfj_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceRefreshJSONWebToken(GenericAPIView):
    """Refresh JWT token
    API View used to refresh JSON Web Token using permanent token.
    The DeviceRefreshJSONWebToken view requires the Permanent-Token header to be set in the request headers.
    """
    serializer_class = DeviceTokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.META)
        if serializer.is_valid(raise_exception=True):
            data = jwt_devices_response_payload_handler(request=request, **serializer.validated_data)
            return Response(data, status=status.HTTP_200_OK)


class DeviceLogout(DestroyAPIView):
    """Logout user by deleting Device.
    The DeviceLogout view requires the Device-Id header to be set in the request headers.
    """
    queryset = Device.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.get_queryset().get(user=self.request.user, id=self.request.META["HTTP_DEVICE_ID"])
        except KeyError:
            raise ValidationError(_("Device-Id header must be present in the request headers."))
        except Device.DoesNotExist:
            raise NotFound(_("Device does not exist."))


class DeviceViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    Simple viewset to list and delete Device objects related to user.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


obtain_jwt_token = ObtainJSONWebTokenAPIView.as_view()
device_refresh_token = DeviceRefreshJSONWebToken.as_view()
device_logout = DeviceLogout.as_view()
