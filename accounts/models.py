from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from tenants.models import Tenant

# Create your models here.

class TenantUser(AbstractUser):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tenant=models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name='users')
    name=models.CharField(max_length=150,blank=True)
    email=models.EmailField()
    created_at=models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["tenant", "email"], name="uniq_tenantuser_email_per_tenant",)]

    def __str__(self):
        return f"Username : {self.username} Email {self.email}"
