from rest_framework import serializers

from apps.kyc.models import KYCDocument


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = [
            "id",
            "document_type",
            "document_file",
            "status",
            "extracted_data",
            "rejection_reason",
            "uploaded_at",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "extracted_data",
            "rejection_reason",
            "uploaded_at",
            "processed_at",
        ]