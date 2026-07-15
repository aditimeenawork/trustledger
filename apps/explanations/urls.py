from django.urls import path

from apps.explanations.views import RiskEventExplanationView

urlpatterns = [
    path(
        "risk-events/<int:risk_event_id>/",
        RiskEventExplanationView.as_view(),
        name="risk-event-explanation",
    ),
]