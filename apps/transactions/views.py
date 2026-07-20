from django.db import transaction as db_transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsOwnerOrInternalRole, is_internal_user
from apps.risk_engine.tasks import evaluate_transaction_risk
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services import create_transaction


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsOwnerOrInternalRole]

    def get_queryset(self):
        user = self.request.user

        if is_internal_user(user):
            return Transaction.objects.select_related("user").all()

        return Transaction.objects.select_related("user").filter(user=user)

    def perform_create(self, serializer):
        transaction = create_transaction(
            user=self.request.user,
            amount=serializer.validated_data["amount"],
            currency=serializer.validated_data["currency"],
            device_fingerprint=serializer.validated_data["device_fingerprint"],
            geo_location=serializer.validated_data["geo_location"],
        )

        serializer.instance = transaction

        db_transaction.on_commit(
            lambda: evaluate_transaction_risk.delay(transaction.id)
        )

    @action(detail=True, methods=["get"])
    def risk(self, request, pk=None):
        transaction = self.get_object()
        latest_event = transaction.risk_events.order_by("-created_at").first()

        if latest_event is None:
            return Response(
                {
                    "transaction_id": transaction.id,
                    "status": transaction.status,
                    "risk_status": "PENDING",
                    "detail": "Risk evaluation has not completed yet.",
                }
            )

        explanation = getattr(latest_event, "explanation", None)

        return Response(
            {
                "transaction_id": transaction.id,
                "status": transaction.status,
                "risk_score": latest_event.risk_score,
                "risk_tier": latest_event.risk_tier,
                "risk_event_created_at": latest_event.created_at,
                "explanation": explanation.parsed_explanation if explanation else None,
            }
        )