from django.db import models


class WebhookEvent(models.Model):
    class EventType(models.TextChoices):
        PAYMENT_STATUS = "PAYMENT_STATUS", "Payment Status"
        KYC_STATUS = "KYC_STATUS", "KYC Status"
        UNKNOWN = "UNKNOWN", "Unknown"

    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(
        max_length=40,
        choices=EventType.choices,
        default=EventType.UNKNOWN,
    )
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    processing_result = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["processed"]),
        ]

    def __str__(self):
        return f"WebhookEvent(event_id={self.event_id}, processed={self.processed})"