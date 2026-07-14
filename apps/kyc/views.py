from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser

from apps.kyc.models import KYCDocument
from apps.kyc.serializers import KYCDocumentSerializer
from apps.kyc.services import verify_kyc_document


class KYCDocumentUploadView(generics.CreateAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        verify_kyc_document(document)


class MyKYCDocumentsView(generics.ListAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user).order_by("-uploaded_at")