from django.utils import timezone

from apps.accounts.models import KYCProfile
from apps.kyc.models import KYCDocument


def mock_extract_document_data(document):
    file_name = document.document_file.name.lower()

    return {
        "document_type": document.document_type,
        "file_name": document.document_file.name,
        "contains_required_fields": "invalid" not in file_name,
    }


def verify_kyc_document(document):
    document.status = KYCDocument.Status.PROCESSING
    document.save(update_fields=["status"])

    extracted_data = mock_extract_document_data(document)
    is_valid = extracted_data["contains_required_fields"]

    document.extracted_text = f"Mock OCR output for {document.document_type}"
    document.extracted_data = extracted_data
    document.processed_at = timezone.now()

    profile = document.user.kyc_profile
    profile.id_type = document.document_type
    profile.attempt_count += 1

    if is_valid:
        document.status = KYCDocument.Status.VERIFIED
        profile.verification_status = KYCProfile.VerificationStatus.VERIFIED
        profile.verified_at = timezone.now()
        document.rejection_reason = ""
    else:
        document.status = KYCDocument.Status.REJECTED
        profile.verification_status = KYCProfile.VerificationStatus.REJECTED
        profile.verified_at = None
        document.rejection_reason = "Document failed mock verification."

    document.save()
    profile.save(
        update_fields=[
            "id_type",
            "attempt_count",
            "verification_status",
            "verified_at",
        ]
    )

    return document