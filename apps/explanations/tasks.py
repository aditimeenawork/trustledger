from celery import shared_task

from apps.audit.models import RiskEvent
from apps.explanations.services import generate_explanation_for_risk_event


@shared_task
def generate_explanation(risk_event_id):
    risk_event = (
        RiskEvent.objects
        .select_related("transaction")
        .prefetch_related("rule_triggers")
        .get(id=risk_event_id)
    )

    return generate_explanation_for_risk_event(risk_event)