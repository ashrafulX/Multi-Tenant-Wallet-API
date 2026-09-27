from django.shortcuts import render
from .serializers import TenantModelSerializer,TenantApiKeySerializer,TenantUpdateSerializer
from rest_framework import viewsets
from .models import Tenant
from rest_framework.permissions import IsAdminUser,AllowAny
# Create your views here.

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return TenantUpdateSerializer

        if self.request.user.is_staff:
            return TenantApiKeySerializer

        return TenantModelSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy",'create']:
            return [IsAdminUser()]
        return [AllowAny()]





