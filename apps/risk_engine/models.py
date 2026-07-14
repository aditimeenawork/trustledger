from django.db import models


class RuleTrigger(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    risk_event = models.ForeignKey(
        "audit.RiskEvent",
        on_delete=models.CASCADE,
        related_name="rule_triggers",
    )
    rule_code = models.CharField(max_length=50)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rule_code"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self):
        return f"{self.rule_code} - {self.severity}"