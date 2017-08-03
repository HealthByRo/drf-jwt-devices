import datetime

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "JWT_DEVICES", None)

DEFAULTS = {
    "JWT_PERMANENT_TOKEN_AUTH": True,
    "JWT_PERMANENT_TOKEN_EXPIRATION_ACCURACY": datetime.timedelta(minutes=30),
    "JWT_PERMANENT_TOKEN_EXPIRATION_DELTA": datetime.timedelta(days=7),

    "JWT_DEVICES_RESPONSE_PAYLOAD_HANDLER":
    "jwt_devices.utils.jwt_devices_response_payload_handler",

    "JWT_DEVICES_PAYLOAD_HANDLER":
    "jwt_devices.utils.jwt_devices_payload_handler",

    "JWT_DEVICES_ENCODE_HANDLER":
    "jwt_devices.utils.jwt_devices_encode_handler",

    "JWT_DEVICES_DECODE_HANDLER":
    "jwt_devices.utils.jwt_devices_decode_handler",
}

IMPORT_STRINGS = (
    "JWT_DEVICES_RESPONSE_PAYLOAD_HANDLER",
    "JWT_DEVICES_PAYLOAD_HANDLER",
    "JWT_DEVICES_ENCODE_HANDLER",
    "JWT_DEVICES_DECODE_HANDLER",
)
# List of settings that may be in string import notation.

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
