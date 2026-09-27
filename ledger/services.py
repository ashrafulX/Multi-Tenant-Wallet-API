from uuid import uuid4
from django.db import IntegrityError

from ledger.models import Transaction, IdempotencyKey


class IdempotencyConflict(Exception):
    pass


class LedgerService:
    @staticmethod
    def record(tenant, wallet, type, amount, balance_after, idempotency_key_obj=None, transfer_group_id=None):
        return Transaction.objects.create(id=uuid4(),tenant=tenant,wallet=wallet,type=type,amount=amount,balance_after=balance_after,idempotency_key=idempotency_key_obj,
            transfer_group_id=transfer_group_id,  
        )
    @staticmethod
    def get_transaction_history(tenant, wallet_id):
        return Transaction.objects.filter(
            tenant=tenant,
            wallet_id=wallet_id,
        ).order_by("-created_at")


class IdempotencyGuard:
    @staticmethod
    def check_or_lock(tenant, key, scope, fingerprint):
        existing = IdempotencyKey.objects.select_for_update().filter( tenant=tenant, key=key, scope=scope,).first()
        if existing is None:
            return None

        if existing.request_fingerprint != fingerprint:
            raise IdempotencyConflict("This idempotency_key was already used with a different request.")

        return existing

    @staticmethod
    def finalize(tenant, key, scope, fingerprint, wallet, response_status, response_body):
        return IdempotencyKey.objects.create( id=uuid4(),tenant=tenant, key=key, scope=scope,request_fingerprint=fingerprint, wallet=wallet, response_status=response_status,response_body=response_body,)