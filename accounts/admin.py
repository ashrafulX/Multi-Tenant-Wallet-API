from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import TenantUser

@admin.register(TenantUser)
class TenantUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "tenant",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "tenant",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "name",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Tenant Information",
            {
                "fields": (
                    "tenant",
                    "name",
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Tenant Information",
            {
                "fields": (
                    "tenant",
                    "name",
                )
            }
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("tenant")