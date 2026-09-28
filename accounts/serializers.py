from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'tenant', 'password']
        read_only_fields = ['tenant']

    def validate(self, attrs):
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None)
        if not tenant:
            raise serializers.ValidationError({"tenant": "Valid tenant is required."})
        attrs["tenant"] = tenant
        return super().validate(attrs)

    def perform_create(self, validated_data):
        request = self.context.get("request")
        if request and getattr(request, "tenant", None):
            validated_data["tenant"] = request.tenant
        return super().perform_create(validated_data)