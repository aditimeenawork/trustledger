from rest_framework import serializers

from apps.audit.models import RiskEvent
from apps.risk_engine.models import RuleTrigger


class RuleTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleTrigger
        fields = ["id", "rule_code", "description", "severity", "created_at"]


class RiskEventSerializer(serializers.ModelSerializer):
    rule_triggers = RuleTriggerSerializer(many=True, read_only=True)

    class Meta:
        model = RiskEvent
        fields = [
            "id",
            "transaction",
            "risk_score",
            "risk_tier",
            "supersedes",
            "rule_triggers",
            "created_at",
        ]