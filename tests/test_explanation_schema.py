import pytest

from apps.explanations.models import ExplanationLog
from apps.explanations.services import (
    ExplanationValidationError,
    generate_explanation_for_risk_event,
    validate_and_parse_json,
)
from tests.factories import RiskEventFactory, RuleTriggerFactory


@pytest.mark.django_db
def test_valid_explanation_json_passes_schema():
    raw = """
    {
      "summary": "Transaction was assigned a HIGH risk tier.",
      "risk_tier": "HIGH",
      "key_factors": ["User has not completed verified KYC."],
      "recommendation": "REJECT"
    }
    """

    parsed = validate_and_parse_json(raw)

    assert parsed["risk_tier"] == "HIGH"
    assert parsed["recommendation"] == "REJECT"


@pytest.mark.django_db
def test_invalid_explanation_json_fails_schema():
    raw = '{"summary": "Missing required fields"}'

    with pytest.raises(ExplanationValidationError):
        validate_and_parse_json(raw)


@pytest.mark.django_db
def test_explanation_generation_falls_back_when_gemini_response_is_invalid(monkeypatch):
    risk_event = RiskEventFactory(risk_score=0.8, risk_tier="HIGH")
    RuleTriggerFactory(risk_event=risk_event)

    monkeypatch.setattr(
        "apps.explanations.services.call_llm_api",
        lambda prompt, risk_data: "not valid json",
    )

    parsed = generate_explanation_for_risk_event(risk_event)

    assert parsed["recommendation"] == "MANUAL_REVIEW"
    assert ExplanationLog.objects.count() == 1