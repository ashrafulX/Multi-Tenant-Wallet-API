from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from ledger.models import Transaction
from ledger.serializers import TransactionSerializer
from config.permissions import IsTenantAuthenticated
# Create your views here.

class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsTenantAuthenticated]
    http_method_names = ["get"]  

    def get_queryset(self):
        queryset = Transaction.objects.filter(tenant=self.request.tenant)
        wallet_id = self.request.query_params.get("wallet_id")
        if wallet_id:
            queryset = queryset.filter(wallet_id=wallet_id)
        return queryset.order_by("-created_at")