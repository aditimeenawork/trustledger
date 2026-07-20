from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser
from apps.accounts.permissions import IsNotReadOnlyAuditor
from apps.kyc.models import KYCDocument
from apps.kyc.serializers import KYCDocumentSerializer
from apps.kyc.services import verify_kyc_document
from apps.kyc.tasks import verify_kyc_document_task


class KYCDocumentUploadView(generics.CreateAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsNotReadOnlyAuditor]
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = "kyc_upload"

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        verify_kyc_document_task.delay(document.id)


class MyKYCDocumentsView(generics.ListAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsNotReadOnlyAuditor]

    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user).order_by("-uploaded_at")