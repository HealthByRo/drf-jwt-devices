from django.contrib import admin

from jwt_devices.models import Device


class DeviceAdmin(admin.ModelAdmin):
    model = Device
    list_display = ["id", "user", "name", "created", "last_request_datetime"]
    list_filter = ["id", "user", "name", "created", "last_request_datetime"]
    search_fields = ["user__email", "name", "details"]
    fields = ["id", "name", "details", "created", "last_request_datetime"]
    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("user")

    def has_add_permission(self, request):
        return False


admin.site.register(Device, DeviceAdmin)
