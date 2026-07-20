from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.accounts.models import KYCProfile
from apps.audit.models import RiskEvent
from apps.explanations.models import ExplanationLog
from apps.transactions.models import Transaction
from apps.webhooks.models import WebhookEvent

User = get_user_model()


def count_by_field(model, field_name):
    return {
        item[field_name]: item["count"]
        for item in model.objects.values(field_name).annotate(count=Count("id"))
    }


def get_dashboard_summary():
    return {
        "users": {
            "total": User.objects.count(),
            "active": User.objects.filter(is_active=True).count(),
            "staff": User.objects.filter(is_staff=True).count(),
            "by_risk_tier": count_by_field(User, "risk_tier"),
        },
        "kyc": {
            "total_profiles": KYCProfile.objects.count(),
            "by_status": count_by_field(KYCProfile, "verification_status"),
            "total_attempts": sum(
                KYCProfile.objects.values_list("attempt_count", flat=True)
            ),
        },
        "transactions": {
            "total": Transaction.objects.count(),
            "by_status": count_by_field(Transaction, "status"),
            "by_currency": count_by_field(Transaction, "currency"),
        },
        "risk": {
            "total_events": RiskEvent.objects.count(),
            "by_tier": count_by_field(RiskEvent, "risk_tier"),
        },
        "explanations": {
            "total": ExplanationLog.objects.count(),
            "by_provider": count_by_field(ExplanationLog, "provider"),
        },
        "webhooks": {
            "total": WebhookEvent.objects.count(),
            "processed": WebhookEvent.objects.filter(processed=True).count(),
            "unprocessed": WebhookEvent.objects.filter(processed=False).count(),
            "by_event_type": count_by_field(WebhookEvent, "event_type"),
        },
    }