from rest_framework.authentication import BaseAuthentication
from tenants.models import Tenant


class TenantAPIKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        request.tenant = None

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return None

        tenant = Tenant.objects.filter(api_key=api_key,is_active=True).first()

        if tenant is None:
            return None

        request.tenant = tenant

        return None