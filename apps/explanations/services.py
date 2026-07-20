import json
import time

import jsonschema
from django.conf import settings
from google import genai

from apps.explanations.models import ExplanationLog


EXPLANATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "summary",
        "risk_tier",
        "key_factors",
        "recommendation",
    ],
    "properties": {
        "summary": {"type": "string"},
        "risk_tier": {
            "type": "string",
            "enum": ["LOW", "MEDIUM", "HIGH"],
        },
        "key_factors": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 5,
        },
        "recommendation": {
            "type": "string",
            "enum": ["APPROVE", "MANUAL_REVIEW", "REJECT"],
        },
    },
}


EXPLANATION_PROMPT_TEMPLATE = """
You are a financial risk explanation assistant for a KYC and transaction fraud system.

Your task:
- Explain why this transaction received its risk tier.
- Use ONLY the structured data provided below.
- Do not invent facts.
- Do not mention rules that are not present in the input.
- Do not expose internal implementation details.
- Return ONLY valid JSON.

The JSON must match this structure:
{{
  "summary": "one sentence plain-English summary",
  "risk_tier": "LOW | MEDIUM | HIGH",
  "key_factors": ["short factual factor", "max 5 items"],
  "recommendation": "APPROVE | MANUAL_REVIEW | REJECT"
}}

Structured risk data:
{risk_data_json}
"""


CORRECTION_PROMPT_TEMPLATE = """
The previous response was invalid and failed JSON schema validation.

Validation error:
{validation_error}

Invalid response:
{invalid_response}

Return ONLY valid JSON matching the required schema.
Do not include markdown.
Do not include explanation outside the JSON object.
Do not invent facts.

Original prompt:
{original_prompt}
"""


class ExplanationValidationError(Exception):
    pass


def build_risk_data(risk_event):
    transaction = risk_event.transaction

    return {
        "risk_event_id": risk_event.id,
        "transaction_id": transaction.id,
        "risk_score": risk_event.risk_score,
        "risk_tier": risk_event.risk_tier,
        "transaction": {
            "amount": str(transaction.amount),
            "currency": transaction.currency,
            "status": transaction.status,
            "device_fingerprint": transaction.device_fingerprint,
            "geo_location": transaction.geo_location,
            "created_at": transaction.created_at.isoformat(),
        },
        "triggered_rules": [
            {
                "code": trigger.rule_code,
                "severity": trigger.severity,
                "description": trigger.description,
            }
            for trigger in risk_event.rule_triggers.all().order_by("created_at")
        ],
    }


def recommendation_for_tier(risk_tier):
    if risk_tier == "HIGH":
        return "REJECT"

    if risk_tier == "MEDIUM":
        return "MANUAL_REVIEW"

    return "APPROVE"


def build_mock_response(risk_data):
    key_factors = [
        trigger["description"]
        for trigger in risk_data["triggered_rules"][:5]
    ]

    if not key_factors:
        key_factors = ["No deterministic risk rules were triggered."]

    return json.dumps(
        {
            "summary": f"Transaction was assigned a {risk_data['risk_tier']} risk tier based on the available risk signals.",
            "risk_tier": risk_data["risk_tier"],
            "key_factors": key_factors,
            "recommendation": recommendation_for_tier(risk_data["risk_tier"]),
        }
    )


def call_gemini_api(prompt):
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    interaction = client.interactions.create(
        model=settings.EXPLANATION_MODEL_NAME,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": EXPLANATION_SCHEMA,
        },
    )

    return interaction.output_text


def call_llm_api(prompt, risk_data):
    if getattr(settings, "EXPLANATIONS_USE_MOCK_LLM", True):
        return build_mock_response(risk_data)

    return call_gemini_api(prompt)


def validate_and_parse_json(raw_response):
    try:
        parsed = json.loads(raw_response)
        jsonschema.validate(instance=parsed, schema=EXPLANATION_SCHEMA)
        return parsed
    except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
        raise ExplanationValidationError(str(exc)) from exc


def fallback_explanation(risk_event):
    return {
        "summary": "Risk explanation could not be generated reliably and requires manual review.",
        "risk_tier": risk_event.risk_tier,
        "key_factors": ["Explanation generation failed validation."],
        "recommendation": "MANUAL_REVIEW",
    }


def build_correction_prompt(original_prompt, invalid_response, validation_error):
    return CORRECTION_PROMPT_TEMPLATE.format(
        original_prompt=original_prompt,
        invalid_response=invalid_response,
        validation_error=validation_error,
    )


def serialize_llm_attempts(attempts):
    if len(attempts) == 1 and attempts[0].get("raw_response"):
        return attempts[0]["raw_response"]

    return json.dumps(attempts, indent=2)


def generate_explanation_for_risk_event(risk_event):
    existing_log = getattr(risk_event, "explanation", None)

    if existing_log:
        return existing_log.parsed_explanation

    risk_data = build_risk_data(risk_event)
    original_prompt = EXPLANATION_PROMPT_TEMPLATE.format(
        risk_data_json=json.dumps(risk_data, indent=2)
    )

    prompt_used = original_prompt
    attempts = []
    start = time.time()

    try:
        raw_response = call_llm_api(original_prompt, risk_data)
        attempts.append(
            {
                "attempt": "initial",
                "raw_response": raw_response,
            }
        )
        parsed = validate_and_parse_json(raw_response)

    except ExplanationValidationError as first_error:
        attempts[-1]["validation_error"] = str(first_error)

        retry_prompt = build_correction_prompt(
            original_prompt=original_prompt,
            invalid_response=attempts[-1]["raw_response"],
            validation_error=str(first_error),
        )
        prompt_used = retry_prompt

        try:
            retry_raw_response = call_llm_api(retry_prompt, risk_data)
            attempts.append(
                {
                    "attempt": "retry",
                    "raw_response": retry_raw_response,
                }
            )
            parsed = validate_and_parse_json(retry_raw_response)

        except ExplanationValidationError as retry_error:
            attempts[-1]["validation_error"] = str(retry_error)
            parsed = fallback_explanation(risk_event)

        except Exception as retry_error:
            attempts.append(
                {
                    "attempt": "retry",
                    "error": str(retry_error),
                }
            )
            parsed = fallback_explanation(risk_event)

    except Exception as error:
        attempts.append(
            {
                "attempt": "initial",
                "error": str(error),
            }
        )
        parsed = fallback_explanation(risk_event)

    latency_ms = int((time.time() - start) * 1000)

    log = ExplanationLog.objects.create(
        risk_event=risk_event,
        prompt_used=prompt_used,
        raw_llm_response=serialize_llm_attempts(attempts),
        parsed_explanation=parsed,
        provider="gemini" if not settings.EXPLANATIONS_USE_MOCK_LLM else "mock",
        model_name=settings.EXPLANATION_MODEL_NAME,
        latency_ms=latency_ms,
    )

    return log.parsed_explanation