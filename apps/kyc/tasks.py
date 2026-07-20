from celery import shared_task

from apps.kyc.models import KYCDocument
from apps.kyc.services import verify_kyc_document


@shared_task
def verify_kyc_document_task(document_id):
    document = KYCDocument.objects.select_related("user").get(id=document_id)
    verify_kyc_document(document)