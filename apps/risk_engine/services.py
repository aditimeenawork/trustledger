from django.db import transaction as db_transaction

from apps.audit.models import RiskEvent
from apps.risk_engine.anomaly import z_score_anomaly
from apps.risk_engine.models import RuleTrigger
from apps.risk_engine.rules import RULES
from apps.transactions.models import Transaction


SEVERITY_WEIGHTS = {
    "LOW": 0.1,
    "MEDIUM": 0.3,
    "HIGH": 0.5,
}


def calculate_risk_tier(risk_score):
    if risk_score >= 0.7:
        return RiskEvent.RiskTier.HIGH
    if risk_score >= 0.4:
        return RiskEvent.RiskTier.MEDIUM
    return RiskEvent.RiskTier.LOW


def evaluate_transaction(transaction_id):
    transaction = Transaction.objects.select_related("user").get(id=transaction_id)
    user = transaction.user
    kyc_profile = getattr(user, "kyc_profile", None)

    triggered_rules = [
        rule for rule in RULES if rule.evaluate(transaction, user, kyc_profile)
    ]

    anomaly_flag = z_score_anomaly(transaction, user)

    risk_score = sum(SEVERITY_WEIGHTS[rule.severity] for rule in triggered_rules)

    if anomaly_flag:
        risk_score += 0.3

    risk_score = min(risk_score, 1.0)
    risk_tier = calculate_risk_tier(risk_score)

    latest_event = transaction.risk_events.order_by("-created_at").first()

    with db_transaction.atomic():
        risk_event = RiskEvent.objects.create(
            transaction=transaction,
            risk_score=risk_score,
            risk_tier=risk_tier,
            supersedes=latest_event,
        )

        for rule in triggered_rules:
            RuleTrigger.objects.create(
                risk_event=risk_event,
                rule_code=rule.code,
                description=rule.description,
                severity=rule.severity,
            )

        if anomaly_flag:
            RuleTrigger.objects.create(
                risk_event=risk_event,
                rule_code="STATISTICAL_ANOMALY",
                description="Transaction amount has a z-score greater than 3.",
                severity="MEDIUM",
            )

        transaction.status = (
            Transaction.Status.REJECTED
            if risk_tier == RiskEvent.RiskTier.HIGH
            else Transaction.Status.FLAGGED
            if risk_tier == RiskEvent.RiskTier.MEDIUM
            else Transaction.Status.APPROVED
        )
        transaction.save(update_fields=["status"])

    return risk_event