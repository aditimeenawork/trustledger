from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import KYCProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "TrustLedger",
            {
                "fields": (
                    "phone_number",
                    "risk_tier",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "TrustLedger",
            {
                "fields": (
                    "email",
                    "phone_number",
                    "risk_tier",
                )
            },
        ),
    )

    list_display = (
        "id",
        "username",
        "email",
        "phone_number",
        "risk_tier",
        "is_staff",
        "is_active",
    )
    search_fields = (
        "username",
        "email",
        "phone_number",
    )
    list_filter = (
        "risk_tier",
        "is_staff",
        "is_active",
    )


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "id_type",
        "verification_status",
        "attempt_count",
        "verified_at",
        "created_at",
    )
    list_filter = (
        "id_type",
        "verification_status",
    )
    search_fields = (
        "user__username",
        "user__email",
        "user__phone_number",
    )
    readonly_fields = (
        "id_number_hash",
        "created_at",
    )