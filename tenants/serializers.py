from rest_framework import serializers
from .models import Tenant

class TenantModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tenant
        fields=['id','name','is_active','created_at']
        read_only_fields=['id','created_at']


class TenantApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model=Tenant
        fields=['id','name','api_key','is_active','created_at']
        read_only_fields=['id','api_key','created_at']

class TenantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tenant
        fields=['name','is_active']