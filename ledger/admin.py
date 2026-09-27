from django.contrib import admin
from .models import IdempotencyKey, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "wallet",
        "type",
        "amount",
        "balance_after",
        "created_at",
    )

    readonly_fields = (
        "id",
        "tenant",
        "wallet",
        "type",
        "amount",
        "balance_after",
        "transfer_group_id",
        "idempotency_key",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "key",
        "scope",
        "response_status",
        "created_at",
    )

    readonly_fields = (
        "id",
        "tenant",
        "key",
        "scope",
        "request_fingerprint",
        "wallet",
        "response_status",
        "response_body",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False