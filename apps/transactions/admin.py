from django.contrib import admin

from apps.transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "amount",
        "currency",
        "status",
        "device_fingerprint",
        "geo_location",
        "created_at",
    ]
    list_filter = [
        "status",
        "currency",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "user__phone_number",
        "device_fingerprint",
        "geo_location",
    ]
    readonly_fields = [
        "created_at",
    ]