from django.contrib import admin

from apps.webhooks.models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "event_id",
        "event_type",
        "processed",
        "received_at",
        "processed_at",
    ]
    list_filter = [
        "event_type",
        "processed",
        "received_at",
    ]
    search_fields = [
        "event_id",
    ]
    readonly_fields = [
        "event_id",
        "event_type",
        "payload",
        "processed",
        "processing_result",
        "received_at",
        "processed_at",
    ]