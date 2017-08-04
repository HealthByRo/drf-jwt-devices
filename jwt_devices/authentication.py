import jwt
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings as rfj_settings

from jwt_devices.settings import api_settings

jwt_decode_handler = rfj_settings.JWT_DECODE_HANDLER
jwt_devices_decode_handler = api_settings.JWT_DEVICES_DECODE_HANDLER


class PermanentTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            if api_settings.JWT_PERMANENT_TOKEN_AUTH:
                payload = jwt_devices_decode_handler(jwt_value)
            else:
                payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _("Signature has expired.")
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _("Error decoding signature.")
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return user, jwt_value
