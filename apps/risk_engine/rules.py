from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from apps.transactions.models import Transaction


class Rule:
    code = None
    severity = None
    description = None

    def evaluate(self, transaction, user, kyc_profile):
        raise NotImplementedError


class VelocityRule(Rule):
    code = "VELOCITY_EXCEEDED"
    severity = "HIGH"
    description = "User made more than 5 transactions in the last hour."

    def evaluate(self, transaction, user, kyc_profile):
        recent_count = Transaction.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(hours=1),
        ).count()
        return recent_count > 5


class AmountAboveAverageRule(Rule):
    code = "AMOUNT_ABOVE_AVERAGE"
    severity = "MEDIUM"
    description = "Transaction amount is more than 10x the user's average transaction amount."

    def evaluate(self, transaction, user, kyc_profile):
        avg = Transaction.objects.filter(user=user).aggregate(Avg("amount"))["amount__avg"] or 0
        return avg > 0 and transaction.amount > avg * 10


class UnverifiedKYCRule(Rule):
    code = "KYC_NOT_VERIFIED"
    severity = "HIGH"
    description = "User has not completed verified KYC."

    def evaluate(self, transaction, user, kyc_profile):
        return not kyc_profile or kyc_profile.verification_status != "VERIFIED"


class FreshKYCRule(Rule):
    code = "KYC_TOO_RECENT"
    severity = "MEDIUM"
    description = "KYC was verified less than 2 hours before the transaction."

    def evaluate(self, transaction, user, kyc_profile):
        if not kyc_profile or not kyc_profile.verified_at:
            return False
        return timezone.now() - kyc_profile.verified_at < timedelta(hours=2)


RULES = [
    VelocityRule(),
    AmountAboveAverageRule(),
    UnverifiedKYCRule(),
    FreshKYCRule(),
]