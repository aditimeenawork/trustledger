from rest_framework import serializers

from apps.explanations.models import ExplanationLog


class ExplanationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExplanationLog
        fields = [
            "id",
            "risk_event",
            "parsed_explanation",
            "provider",
            "model_name",
            "latency_ms",
            "created_at",
        ]
        read_only_fields = fields