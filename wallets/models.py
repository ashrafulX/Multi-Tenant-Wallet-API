from django.db import models
from tenants.models import Tenant
from accounts.models import TenantUser
from uuid import uuid4
# Create your models here.

class Wallet(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tenant=models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name='wallets')
    owner=models.OneToOneField(TenantUser,on_delete=models.CASCADE,related_name='wallet')
    balance=models.BigIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        constraints=[
            models.CheckConstraint(condition=models.Q(balance__gte=0),
            name='wallet_balance_non_negative',
            )
        ]

    def __str__(self):
        return self.owner.name