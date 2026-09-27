from django.db import models
from uuid import uuid4
import secrets
# Create your models here.

def generate_api_key():
    return secrets.token_hex(32)


class Tenant(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    name=models.CharField(max_length=150)
    api_key=models.CharField(max_length=64,unique=True,default=generate_api_key,editable=False)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-created_at']

    def __str__(self):
        return self.name
    
