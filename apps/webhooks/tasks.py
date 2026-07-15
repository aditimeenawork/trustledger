from celery import shared_task
from django.utils import timezone

from apps.webhooks.models import WebhookEvent


@shared_task
def process_webhook_event(webhook_event_id):
    event = WebhookEvent.objects.get(id=webhook_event_id)

    if event.processed:
        return {
            "status": "already_processed",
            "event_id": event.event_id,
        }

    payload = event.payload

    result = {
        "status": "processed",
        "event_type": event.event_type,
        "external_status": payload.get("status"),
    }

    event.processed = True
    event.processed_at = timezone.now()
    event.processing_result = result
    event.save(update_fields=["processed", "processed_at", "processing_result"])

    return result