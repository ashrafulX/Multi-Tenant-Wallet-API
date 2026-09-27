from rest_framework import serializers
from wallets.models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "tenant", "owner", "balance", "created_at", "updated_at"]
        read_only_fields = fields  


class WalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = []


class MoneyOperationSerializer(serializers.Serializer):

    amount = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=255)


class TransferSerializer(serializers.Serializer):
    to_wallet_id = serializers.UUIDField()
    amount = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=255)
