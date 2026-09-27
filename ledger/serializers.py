from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "tenant", "wallet", "type", "amount", "balance_after", "transfer_group_id", "created_at"]
        read_only_fields = fields