from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.views import APIView
from config.permissions import IsTenantAuthenticated
from wallets.models import Wallet
from wallets.serializers import WalletSerializer,WalletCreateSerializer,MoneyOperationSerializer,TransferSerializer
from wallets.services import WalletService
from ledger.serializers import TransactionSerializer
from ledger.services import LedgerService
from config.pagination import TransactionPagination


class WalletViewSet(ModelViewSet):
    permission_classes = [IsTenantAuthenticated]
    lookup_url_kwarg = "wallet_id"
    http_method_names = ["get", "post"]
    pagination_class = TransactionPagination


    """superuser acces only same tenant"""
    # def get_queryset(self):
    #     queryset = Wallet.objects.filter(
    #         tenant=self.request.tenant
    #     )

    #     if self.request.user.is_staff:
    #         return queryset

    #     return queryset.filter(
    #         owner=self.request.user
    #     )

    def get_queryset(self):
            if self.request.user.is_superuser:
                return Wallet.objects.all()
    
            queryset = Wallet.objects.filter(
                tenant=self.request.tenant
            )
    
            if self.request.user.is_staff:
                return queryset
    
            return queryset.filter(
                owner=self.request.user
            )

  
    def get_serializer_class(self):

        if self.action == "create":
            return WalletCreateSerializer

        if self.action in ["deposit", "withdraw"]:
            return MoneyOperationSerializer

        if self.action == "transfer":
            return TransferSerializer

        return WalletSerializer


    

    def perform_create(self, serializer):
        wallet = WalletService.create_wallet(
            tenant=self.request.tenant,
            owner_id=self.request.user.id,
        )

        serializer.instance = wallet

    @action(detail=True, methods=["post"])
    def deposit(self, request, wallet_id=None):

        wallet = self.get_object()

        serializer = MoneyOperationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        result = WalletService.deposit(
            tenant=request.tenant,
            wallet_id=wallet.id,
            amount=serializer.validated_data["amount"],
            idempotency_key=serializer.validated_data["idempotency_key"],
        )

        return Response(result, status=201)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, wallet_id=None):

        wallet = self.get_object()

        serializer = MoneyOperationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        result = WalletService.withdraw(
            tenant=request.tenant,
            wallet_id=wallet.id,
            amount=serializer.validated_data["amount"],
            idempotency_key=serializer.validated_data["idempotency_key"],
        )

        return Response(result, status=201)

    @action(detail=True, methods=["get"])
    def transactions(self, request, wallet_id=None):

        wallet = self.get_object()

        history = LedgerService.get_transaction_history(
            tenant=request.tenant,
            wallet_id=wallet.id,
        )

        page = self.paginate_queryset(history)

        if page is not None:
            serializer = TransactionSerializer(
                page,
                many=True
            )
            return self.get_paginated_response(
                serializer.data
            )

        serializer = TransactionSerializer(
            history,
            many=True
        )

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def transfer(self, request, wallet_id=None):

        source_wallet = self.get_object()

        serializer = TransferSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        result = WalletService.transfer(
            tenant=request.tenant,
            from_wallet_id=source_wallet.id,
            to_wallet_id=serializer.validated_data["to_wallet_id"],
            amount=serializer.validated_data["amount"],
            idempotency_key=serializer.validated_data["idempotency_key"],
        )

        return Response(result, status=201)
