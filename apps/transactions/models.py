from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        FLAGGED = "FLAGGED", "Flagged"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(
        max_length=3,
        default="INR",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{3}$",
                message="Currency must be a 3-letter uppercase ISO code.",
            )
        ],
    )
    device_fingerprint = models.CharField(max_length=64)
    geo_location = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["currency"]),
        ]

    def __str__(self):
        return f"Transaction(id={self.id}, user={self.user_id}, amount={self.amount} {self.currency})"