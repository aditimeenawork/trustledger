import numpy as np

from apps.transactions.models import Transaction


def z_score_anomaly(transaction, user):
    amounts = list(
        Transaction.objects.filter(user=user)
        .exclude(id=transaction.id)
        .values_list("amount", flat=True)
    )

    if len(amounts) < 5:
        return False

    mean = np.mean(amounts)
    std = np.std(amounts)

    if std == 0:
        return False

    z_score = (float(transaction.amount) - mean) / std
    return abs(z_score) > 3