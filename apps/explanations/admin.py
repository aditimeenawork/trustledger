from django.contrib import admin

from apps.explanations.models import ExplanationLog


@admin.register(ExplanationLog)
class ExplanationLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "risk_event",
        "provider",
        "model_name",
        "latency_ms",
        "created_at",
    ]
    list_filter = [
        "provider",
        "model_name",
        "created_at",
    ]
    search_fields = [
        "risk_event__id",
        "model_name",
    ]
    readonly_fields = [
        "risk_event",
        "prompt_used",
        "raw_llm_response",
        "parsed_explanation",
        "provider",
        "model_name",
        "latency_ms",
        "created_at",
    ]