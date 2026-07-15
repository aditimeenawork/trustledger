from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services import create_transaction

from apps.risk_engine.tasks import evaluate_transaction_risk


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
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

        from apps.risk_engine.tasks import evaluate_transaction_risk

        evaluate_transaction_risk.delay(transaction.id)

    @action(detail=True, methods=["get"])
    def risk(self, request, pk=None):
        transaction = self.get_object()

        risk_events = getattr(transaction, "risk_events", None)

        if risk_events is None:
            return Response(
                {
                    "transaction_id": transaction.id,
                    "status": transaction.status,
                    "risk_status": "NOT_EVALUATED",
                    "detail": "Risk engine has not been connected yet.",
                }
            )

        latest_event = risk_events.order_by("-created_at").first()

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