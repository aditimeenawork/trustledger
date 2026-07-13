from django.utils.crypto import salted_hmac

from apps.accounts.models import KYCProfile


def normalize_id_number(id_number):
    return "".join(str(id_number).split()).upper()


def hash_id_number(id_number):
    normalized = normalize_id_number(id_number)
    return salted_hmac(
        key_salt="trustledger.kyc.id_number",
        value=normalized,
    ).hexdigest()


def create_or_update_kyc_profile(*, user, id_type, id_number):
    id_number_hash = hash_id_number(id_number)

    profile, created = KYCProfile.objects.get_or_create(
        user=user,
        defaults={
            "id_type": id_type,
            "id_number_hash": id_number_hash,
            "attempt_count": 1,
        },
    )

    if not created:
        profile.id_type = id_type
        profile.id_number_hash = id_number_hash
        profile.verification_status = KYCProfile.VerificationStatus.PENDING
        profile.verified_at = None
        profile.attempt_count += 1
        profile.save(
            update_fields=[
                "id_type",
                "id_number_hash",
                "verification_status",
                "verified_at",
                "attempt_count",
            ]
        )

    return profile