from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import RiskEvent
from apps.explanations.serializers import ExplanationLogSerializer
from apps.explanations.tasks import generate_explanation


class RiskEventExplanationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_risk_event(self, request, risk_event_id):
        queryset = RiskEvent.objects.select_related("transaction")

        if not request.user.is_staff:
            queryset = queryset.filter(transaction__user=request.user)

        return get_object_or_404(queryset, id=risk_event_id)

    def get(self, request, risk_event_id):
        risk_event = self.get_risk_event(request, risk_event_id)
        explanation = getattr(risk_event, "explanation", None)

        if explanation is None:
            generate_explanation.delay(risk_event.id)

            return Response(
                {
                    "status": "PENDING",
                    "detail": "Explanation generation has been queued.",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(ExplanationLogSerializer(explanation).data)