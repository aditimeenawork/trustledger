import pytest

from apps.webhooks.models import WebhookEvent


@pytest.mark.django_db
def test_duplicate_webhook_event_is_ignored(api_client, monkeypatch):
    queued_events = []

    monkeypatch.setattr(
        "apps.webhooks.views.process_webhook_event.delay",
        lambda event_id: queued_events.append(event_id),
    )

    payload = {
        "event_id": "evt_duplicate_test",
        "event_type": "PAYMENT_STATUS",
        "status": "settled",
        "transaction_id": 1,
    }

    first_response = api_client.post("/api/webhooks/gateway/", payload, format="json")
    second_response = api_client.post("/api/webhooks/gateway/", payload, format="json")

    assert first_response.status_code == 202
    assert first_response.data["status"] == "accepted"

    assert second_response.status_code == 200
    assert second_response.data["status"] == "duplicate_ignored"

    assert WebhookEvent.objects.count() == 1
    assert len(queued_events) == 1