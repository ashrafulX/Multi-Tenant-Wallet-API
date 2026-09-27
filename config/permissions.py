from rest_framework.permissions import BasePermission
from tenants.models import Tenant


class IsTenantAuthenticated(BasePermission):

    message = "Invalid or inactive tenant."

    def has_permission(self, request, view):

        api_key = request.headers.get("X-API-Key")

        if api_key:
            tenant = Tenant.objects.filter(
                api_key=api_key,
                is_active=True
            ).first()

            if tenant is None:
                return False

            if not request.user.is_authenticated:
                return False

            if request.user.tenant_id != tenant.id:
                return False

            request.tenant = tenant
            return True

        if not request.user.is_authenticated:
            return False

        tenant = request.user.tenant

        if not tenant.is_active:
            return False

        request.tenant = tenant

        return True