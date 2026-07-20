import pytest

from tests.factories import RiskEventFactory


@pytest.mark.django_db
def test_risk_event_cannot_be_updated():
    risk_event = RiskEventFactory(risk_score=0.4, risk_tier="MEDIUM")

    risk_event.risk_score = 0.9

    with pytest.raises(ValueError):
        risk_event.save()