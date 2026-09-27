from django.db import models
from uuid import uuid4
from tenants.models import Tenant
from wallets.models import Wallet
# Create your models here.

class IdempotencyKey(models.Model):
    DEPOSIT='Deposit'
    WITHDRAWAL='Withdrawal'
    TRANSFER='Transfer'

    IDEMPOTENCY_SCOPE = [
    (DEPOSIT, "Deposit"),
    (WITHDRAWAL, "Withdrawal"),
    (TRANSFER, "Transfer"),
    ]

    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tenant=models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name='idempotency_keys')
    key=models.CharField(max_length=255)
    scope=models.CharField(max_length=20,choices=IDEMPOTENCY_SCOPE)
    request_fingerprint=models.CharField(max_length=64)
    wallet=models.ForeignKey(Wallet,on_delete=models.SET_NULL,null=True,blank=True, related_name="idempotency_keys")
    response_status = models.PositiveSmallIntegerField()
    response_body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Transaction(models.Model):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"

    TRANSACTION_TYPE=[
        (DEPOSIT,"Deposit"),
        (WITHDRAWAL,"Withdrawal"),
        (TRANSFER_OUT,"Transfer Out"),
        (TRANSFER_IN,"Transfer In"),
    ]

    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tenant=models.ForeignKey(Tenant,on_delete=models.PROTECT,related_name='transactions')
    wallet=models.ForeignKey(Wallet,on_delete=models.PROTECT,related_name='transactions')
    type=models.CharField(max_length=20,choices=TRANSACTION_TYPE)
    amount=models.BigIntegerField()
    balance_after=models.BigIntegerField()
    transfer_group_id=models.UUIDField(null=True,blank=True,db_index=True,default=uuid4)
    idempotency_key=models.ForeignKey(IdempotencyKey,null=True,blank=True,on_delete=models.PROTECT,related_name="transactions",)
    created_at=models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="transaction_amount_positive",),]

    def __str__(self):
        return f"{self.type} - {self.wallet.owner.name} - {self.amount}"