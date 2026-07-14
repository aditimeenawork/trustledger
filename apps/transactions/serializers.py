from rest_framework import serializers

from apps.transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    kyc_status = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "currency",
            "device_fingerprint",
            "geo_location",
            "status",
            "kyc_status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "kyc_status",
            "created_at",
        ]

    def get_kyc_status(self, obj):
        profile = getattr(obj.user, "kyc_profile", None)

        if profile is None:
            return "NOT_SUBMITTED"

        return profile.verification_status

    def validate_currency(self, value):
        return value.upper()

    def validate_device_fingerprint(self, value):
        if not value.strip():
            raise serializers.ValidationError("Device fingerprint is required.")
        return value.strip()

    def validate_geo_location(self, value):
        if not value.strip():
            raise serializers.ValidationError("Geo location is required.")
        return value.strip()