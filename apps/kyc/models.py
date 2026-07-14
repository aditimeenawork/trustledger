
from django.conf import settings
from django.db import models


class KYCDocument(models.Model):
    class DocumentType(models.TextChoices):
        PAN = "PAN", "PAN"
        AADHAAR = "AADHAAR", "Aadhaar"
        PASSPORT = "PASSPORT", "Passport"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        PROCESSING = "PROCESSING", "Processing"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc_documents",
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_file = models.FileField(upload_to="kyc_documents/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)

    extracted_text = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)
    rejection_reason = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_id} - {self.document_type} - {self.status}"