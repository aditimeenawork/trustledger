from django.urls import path
from apps.dashboard.views import AdminDashboardSummaryView

urlpatterns = [
    path("summary/", AdminDashboardSummaryView.as_view(), name="admin-dashboard-summary"),
]