from django.db import models


class ExplanationLog(models.Model):
    risk_event = models.OneToOneField(
        "audit.RiskEvent",
        on_delete=models.CASCADE,
        related_name="explanation",
    )
    prompt_used = models.TextField()
    raw_llm_response = models.TextField()
    parsed_explanation = models.JSONField()
    provider = models.CharField(max_length=30, default="gemini")
    model_name = models.CharField(max_length=80)
    latency_ms = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ExplanationLog(risk_event={self.risk_event_id}, provider={self.provider}, model={self.model_name})"