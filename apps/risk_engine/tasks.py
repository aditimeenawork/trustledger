from celery import shared_task

from apps.risk_engine.services import evaluate_transaction


@shared_task
def evaluate_transaction_risk(transaction_id):
    risk_event = evaluate_transaction(transaction_id)
    return risk_event.id