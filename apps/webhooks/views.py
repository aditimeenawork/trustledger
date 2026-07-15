from django.db import IntegrityError, transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.webhooks.models import WebhookEvent
from apps.webhooks.serializers import WebhookReceiveSerializer
from apps.webhooks.tasks import process_webhook_event


class GatewayWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = WebhookReceiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event_id"]
        event_type = serializer.validated_data["event_type"]
        payload = serializer.validated_data["payload"]

        try:
            with transaction.atomic():
                event, created = WebhookEvent.objects.get_or_create(
                    event_id=event_id,
                    defaults={
                        "event_type": event_type,
                        "payload": payload,
                    },
                )
        except IntegrityError:
            return Response(
                {
                    "status": "duplicate_ignored",
                    "event_id": event_id,
                },
                status=status.HTTP_200_OK,
            )

        if not created:
            return Response(
                {
                    "status": "duplicate_ignored",
                    "event_id": event.event_id,
                },
                status=status.HTTP_200_OK,
            )

        process_webhook_event.delay(event.id)

        return Response(
            {
                "status": "accepted",
                "event_id": event.event_id,
            },
            status=status.HTTP_202_ACCEPTED,
        )