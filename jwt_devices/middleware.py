from django.http.response import JsonResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from jwt_devices import views
from jwt_devices.settings import api_settings


class PermittedHeadersMiddleware(object):
    """
    Middleware used to disallow sending the permanent_token header in other requests than during permanent token
    refresh to make sure naive FE developers do not send the fragile permanent token with each request.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if self.get_response:
            return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_cls = getattr(view_func, "cls", None)
        if (view_cls and api_settings.JWT_PERMANENT_TOKEN_AUTH and request.META.get("HTTP_PERMANENT_TOKEN") and view_cls != views.DeviceRefreshJSONWebToken):
            return JsonResponse({
                "HTTP_PERMANENT_TOKEN": {
                    "details": _("Using the Permanent-Token header is disallowed for {}").format(type(view_cls))
                }
            }, status=status.HTTP_400_BAD_REQUEST)
