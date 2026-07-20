from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import KYCProfile
from apps.audit.models import RiskEvent
from apps.risk_engine.models import RuleTrigger
from apps.transactions.models import Transaction
from apps.webhooks.models import WebhookEvent

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    phone_number = factory.Sequence(lambda n: f"+919000{n:06d}")
    password = factory.PostGenerationMethodCall("set_password", "TestPass123")


class KYCProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KYCProfile

    user = factory.SubFactory(UserFactory)
    id_type = "PAN"
    id_number_hash = "hashed-id-number"
    verification_status = "VERIFIED"
    verified_at = factory.LazyFunction(timezone.now)
    attempt_count = 1


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    amount = Decimal("1000.00")
    currency = "INR"
    device_fingerprint = "device-test-123"
    geo_location = "Mumbai, IN"


class RiskEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskEvent

    transaction = factory.SubFactory(TransactionFactory)
    risk_score = 0.5
    risk_tier = "MEDIUM"


class RuleTriggerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleTrigger

    risk_event = factory.SubFactory(RiskEventFactory)
    rule_code = "KYC_NOT_VERIFIED"
    description = "User has not completed verified KYC."
    severity = "HIGH"


class WebhookEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WebhookEvent

    event_id = factory.Sequence(lambda n: f"evt_{n}")
    event_type = "PAYMENT_STATUS"
    payload = factory.LazyFunction(dict)