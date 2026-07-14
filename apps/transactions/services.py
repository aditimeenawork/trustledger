from apps.transactions.models import Transaction


def create_transaction(*, user, amount, currency, device_fingerprint, geo_location):
    return Transaction.objects.create(
        user=user,
        amount=amount,
        currency=currency.upper(),
        device_fingerprint=device_fingerprint,
        geo_location=geo_location,
    )