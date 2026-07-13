from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class RiskTier(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9]{10,15}$",
                message="Enter a valid phone number with 10 to 15 digits.",
            )
        ],
    )
    risk_tier = models.CharField(
        max_length=10,
        choices=RiskTier.choices,
        default=RiskTier.LOW,
    )

    REQUIRED_FIELDS = ["email", "phone_number"]

    def __str__(self):
        return self.username


class KYCProfile(models.Model):
    class IDType(models.TextChoices):
        PAN = "PAN", "PAN"
        AADHAAR = "AADHAAR", "Aadhaar"
        PASSPORT = "PASSPORT", "Passport"

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="kyc_profile",
    )
    id_type = models.CharField(max_length=20, choices=IDType.choices)
    id_number_hash = models.CharField(max_length=128)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KYCProfile(user={self.user_id}, status={self.verification_status})"