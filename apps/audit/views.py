from rest_framework import generics

from apps.accounts.permissions import IsInternalRole
from apps.audit.models import RiskEvent
from apps.audit.serializers import RiskEventSerializer


class TransactionRiskEventHistoryView(generics.ListAPIView):
    serializer_class = RiskEventSerializer
    permission_classes = [IsInternalRole]

    def get_queryset(self):
        transaction_id = self.kwargs["transaction_id"]

        return (
            RiskEvent.objects
            .filter(transaction_id=transaction_id)
            .select_related("transaction", "transaction__user")
            .prefetch_related("rule_triggers")
        )