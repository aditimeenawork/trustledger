from django.contrib import admin

from apps.kyc.models import KYCDocument


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "document_type",
        "status",
        "uploaded_at",
        "processed_at",
    ]
    list_filter = ["document_type", "status"]
    search_fields = ["user__username", "user__email", "user__phone_number"]
    readonly_fields = [
        "extracted_text",
        "extracted_data",
        "rejection_reason",
        "uploaded_at",
        "processed_at",
    ]