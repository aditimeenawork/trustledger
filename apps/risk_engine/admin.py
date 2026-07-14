from django.contrib import admin

from apps.risk_engine.models import RuleTrigger


@admin.register(RuleTrigger)
class RuleTriggerAdmin(admin.ModelAdmin):
    list_display = ["id", "risk_event", "rule_code", "severity", "created_at"]
    list_filter = ["rule_code", "severity"]
    readonly_fields = ["risk_event", "rule_code", "description", "severity", "created_at"]