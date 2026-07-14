from django.urls import path

from apps.audit.views import TransactionRiskEventHistoryView

urlpatterns = [
    path(
        "risk-events/<int:transaction_id>/",
        TransactionRiskEventHistoryView.as_view(),
        name="transaction-risk-event-history",
    ),
]