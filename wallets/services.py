from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from accounts.models import TenantUser
from wallets.models import Wallet
from ledger.models import Transaction, IdempotencyKey
import uuid
import hashlib
import json
from config.exceptions import WalletAlreadyExists
from rest_framework.exceptions import ValidationError

class WalletService:

    @staticmethod
    def create_wallet(tenant, owner_id):
        owner = get_object_or_404(
            TenantUser,
            id=owner_id,
            tenant=tenant
        )

        try:
            with transaction.atomic():
                return Wallet.objects.create(
                    tenant=tenant,
                    owner=owner,
                    balance=0
                )
        except IntegrityError:
            raise WalletAlreadyExists(
                "This user already has a wallet."
            )

    @staticmethod
    @transaction.atomic
    def deposit(
        tenant,
        wallet_id,
        amount,
        idempotency_key
    ):
        wallet = Wallet.objects.select_for_update().filter(
            id=wallet_id,
            tenant=tenant).first()

        if wallet is None:
            raise ValueError("Wallet not found.")

        existing = IdempotencyKey.objects.filter(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.DEPOSIT
        ).first()

        if existing:
            return existing.response_body

        wallet.balance += amount
        wallet.save(update_fields=["balance", "updated_at"])

        idempotency = IdempotencyKey.objects.create(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.DEPOSIT,
            request_fingerprint="deposit",
            wallet=wallet,
            response_status=201,
            response_body={
                "wallet_id": str(wallet.id),
                "amount": amount,
                "balance": wallet.balance,
            },
        )

        Transaction.objects.create(
            tenant=tenant,
            wallet=wallet,
            type=Transaction.DEPOSIT,
            amount=amount,
            balance_after=wallet.balance,
            idempotency_key=idempotency,
        )

        return idempotency.response_body

    @staticmethod
    @transaction.atomic
    def withdraw(
        tenant,
        wallet_id,
        amount,
        idempotency_key
    ):
        wallet = Wallet.objects.select_for_update().filter(
            id=wallet_id,
            tenant=tenant
        ).first()

        if wallet is None:
            raise ValueError("Wallet not found.")

        existing = IdempotencyKey.objects.filter(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.WITHDRAWAL
        ).first()

        if existing:
            return existing.response_body

        if wallet.balance < amount:
            raise ValueError("Insufficient funds.")

        wallet.balance -= amount
        wallet.save(update_fields=["balance", "updated_at"])

        idempotency = IdempotencyKey.objects.create(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.WITHDRAWAL,
            request_fingerprint="withdraw",
            wallet=wallet,
            response_status=201,
            response_body={
                "wallet_id": str(wallet.id),
                "amount": amount,
                "balance": wallet.balance,
            },
        )

        Transaction.objects.create(
            tenant=tenant,
            wallet=wallet,
            type=Transaction.WITHDRAWAL,
            amount=amount,
            balance_after=wallet.balance,
            idempotency_key=idempotency,
        )

        return idempotency.response_body

    @staticmethod
    @transaction.atomic
    def transfer(tenant,from_wallet_id,to_wallet_id, amount, idempotency_key,):
        if from_wallet_id == to_wallet_id:
            raise ValidationError(
                "Source and destination wallets must be different."
            )

        wallet_ids = sorted(
            [from_wallet_id, to_wallet_id],
            key=str,
        )

        wallets = (
            Wallet.objects
            .select_for_update()
            .filter(
                tenant=tenant,
                id__in=wallet_ids,
            )
            .order_by("id")
        )

        wallet_map = {
            str(wallet.id): wallet
            for wallet in wallets
        }

        if len(wallet_map) != 2:
            raise ValidationError(
                "Source or destination wallet not found."
            )

        from_wallet = wallet_map[str(from_wallet_id)]
        to_wallet = wallet_map[str(to_wallet_id)]

        fingerprint_data = {
            "from_wallet_id": str(from_wallet.id),
            "to_wallet_id": str(to_wallet.id),
            "amount": amount,
        }

        request_fingerprint = hashlib.sha256(
            json.dumps(
                fingerprint_data,
                sort_keys=True,
            ).encode()
        ).hexdigest()

        existing = IdempotencyKey.objects.filter(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.TRANSFER,
        ).first()

        if existing:
            if existing.request_fingerprint != request_fingerprint:
                raise ValidationError(
                    "This idempotency key was already used "
                    "for a different request."
                )

            return existing.response_body

        if from_wallet.balance < amount:
            raise ValidationError(
                "Insufficient funds."
            )

        transfer_group_id = uuid.uuid4()

        from_wallet.balance -= amount
        to_wallet.balance += amount

        from_wallet.save(
            update_fields=["balance", "updated_at"]
        )

        to_wallet.save(
            update_fields=["balance", "updated_at"]
        )

        idempotency = IdempotencyKey.objects.create(
            tenant=tenant,
            key=idempotency_key,
            scope=IdempotencyKey.TRANSFER,
            request_fingerprint=request_fingerprint,
            wallet=from_wallet,
            response_status=201,
            response_body={
                "transfer_group_id": str(transfer_group_id),
                "from_wallet_id": str(from_wallet.id),
                "to_wallet_id": str(to_wallet.id),
                "amount": amount,
                "from_balance": from_wallet.balance,
                "to_balance": to_wallet.balance,
            },
        )

        Transaction.objects.create(
            tenant=tenant,
            wallet=from_wallet,
            type=Transaction.TRANSFER_OUT,
            amount=amount,
            balance_after=from_wallet.balance,
            transfer_group_id=transfer_group_id,
            idempotency_key=idempotency,
        )

        Transaction.objects.create(
            tenant=tenant,
            wallet=to_wallet,
            type=Transaction.TRANSFER_IN,
            amount=amount,
            balance_after=to_wallet.balance,
            transfer_group_id=transfer_group_id,
            idempotency_key=idempotency,
        )

        return idempotency.response_body