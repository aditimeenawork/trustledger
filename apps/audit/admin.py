from django.contrib import admin

from apps.audit.models import RiskEvent


@admin.register(RiskEvent)
class RiskEventAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "risk_score", "risk_tier", "supersedes", "created_at"]
    list_filter = ["risk_tier", "created_at"]
    readonly_fields = ["transaction", "risk_score", "risk_tier", "supersedes", "created_at"]