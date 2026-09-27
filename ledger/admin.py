from django.contrib import admin
from .models import IdempotencyKey,Transaction
# Register your models here.

admin.site.register(IdempotencyKey)
admin.site.register(Transaction)