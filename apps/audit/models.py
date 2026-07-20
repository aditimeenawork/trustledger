from django.db import models


class RiskEvent(models.Model):
    class RiskTier(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    transaction = models.ForeignKey(
        "transactions.Transaction",
        on_delete=models.PROTECT,
        related_name="risk_events",
    )
    risk_score = models.FloatField()
    risk_tier = models.CharField(max_length=10, choices=RiskTier.choices)
    supersedes = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="superseded_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["transaction", "-created_at"]),
            models.Index(fields=["risk_tier"]),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("RiskEvent records are immutable and cannot be edited.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"RiskEvent(transaction={self.transaction_id}, tier={self.risk_tier}, score={self.risk_score})"

    def delete(self, *args, **kwargs):
        raise ValueError("RiskEvent records are immutable and cannot be deleted.")
