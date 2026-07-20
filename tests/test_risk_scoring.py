import pytest

from apps.audit.models import RiskEvent
from apps.risk_engine.models import RuleTrigger
from apps.risk_engine.services import evaluate_transaction
from tests.factories import TransactionFactory, UserFactory


@pytest.mark.django_db
def test_evaluate_transaction_creates_risk_event_and_rule_trigger(
    monkeypatch,
    django_capture_on_commit_callbacks,
):
    queued_explanations = []

    monkeypatch.setattr(
        "apps.explanations.tasks.generate_explanation.delay",
        lambda risk_event_id: queued_explanations.append(risk_event_id),
    )

    user = UserFactory()
    transaction = TransactionFactory(user=user)

    with django_capture_on_commit_callbacks(execute=True):
        risk_event = evaluate_transaction(transaction.id)

    transaction.refresh_from_db()

    assert RiskEvent.objects.count() == 1
    assert RuleTrigger.objects.count() >= 1
    assert risk_event.transaction == transaction
    assert risk_event.risk_tier == "MEDIUM"
    assert transaction.status == "FLAGGED"
    assert queued_explanations == [risk_event.id]