from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsInternalRole
from apps.dashboard.services import get_dashboard_summary


class AdminDashboardSummaryView(APIView):
    permission_classes = [IsInternalRole]

    def get(self, request):
        return Response(get_dashboard_summary())