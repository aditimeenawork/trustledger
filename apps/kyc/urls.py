from django.urls import path

from apps.kyc.views import KYCDocumentUploadView, MyKYCDocumentsView

urlpatterns = [
    path("upload/", KYCDocumentUploadView.as_view(), name="kyc-upload"),
    path("documents/", MyKYCDocumentsView.as_view(), name="kyc-documents"),
]