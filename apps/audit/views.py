from rest_framework import generics, permissions
from apps.audit.models import RiskEvent
from apps.audit.serializers import RiskEventSerializer


class TransactionRiskEventHistoryView(generics.ListAPIView):
    serializer_class = RiskEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        transaction_id = self.kwargs["transaction_id"]

        queryset = RiskEvent.objects.filter(transaction_id=transaction_id).prefetch_related(
            "rule_triggers"
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(transaction__user=self.request.user)