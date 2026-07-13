from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import KYCProfile
from apps.accounts.services import create_or_update_kyc_profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "risk_tier",
            "first_name",
            "last_name",
        ]
        read_only_fields = [
            "id",
            "risk_tier",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class KYCProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCProfile
        fields = [
            "id",
            "id_type",
            "verification_status",
            "verified_at",
            "attempt_count",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "verification_status",
            "verified_at",
            "attempt_count",
            "created_at",
        ]


class KYCProfileSubmitSerializer(serializers.Serializer):
    id_type = serializers.ChoiceField(choices=KYCProfile.IDType.choices)
    id_number = serializers.CharField(write_only=True, min_length=4, max_length=40)

    def save(self, **kwargs):
        user = self.context["request"].user
        return create_or_update_kyc_profile(
            user=user,
            id_type=self.validated_data["id_type"],
            id_number=self.validated_data["id_number"],
        )