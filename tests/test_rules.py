from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.risk_engine.rules import (
    AmountAboveAverageRule,
    FreshKYCRule,
    UnverifiedKYCRule,
    VelocityRule,
)
from tests.factories import KYCProfileFactory, TransactionFactory, UserFactory


@pytest.mark.django_db
def test_unverified_kyc_rule_triggers_without_kyc_profile():
    user = UserFactory()
    transaction = TransactionFactory(user=user)

    assert UnverifiedKYCRule().evaluate(transaction, user, None) is True


@pytest.mark.django_db
def test_fresh_kyc_rule_triggers_for_recent_verification():
    profile = KYCProfileFactory(verified_at=timezone.now() - timedelta(minutes=30))
    transaction = TransactionFactory(user=profile.user)

    assert FreshKYCRule().evaluate(transaction, profile.user, profile) is True


@pytest.mark.django_db
def test_velocity_rule_triggers_after_many_recent_transactions():
    user = UserFactory()

    for _ in range(6):
        TransactionFactory(user=user)

    transaction = TransactionFactory(user=user)

    assert VelocityRule().evaluate(transaction, user, None) is True


@pytest.mark.django_db
def test_amount_above_average_rule_triggers_for_large_transaction():
    user = UserFactory()

    for _ in range(20):
        TransactionFactory(user=user, amount=Decimal("100.00"))

    transaction = TransactionFactory(user=user, amount=Decimal("10000.00"))

    assert AmountAboveAverageRule().evaluate(transaction, user, None) is True