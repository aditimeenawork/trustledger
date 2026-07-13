from django.urls import path

from apps.accounts.views import (
    KYCProfileView,
    KYCStatusView,
    MeView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("me/", MeView.as_view(), name="account-me"),
    path("kyc-profile/", KYCProfileView.as_view(), name="account-kyc-profile"),
    path("kyc-status/", KYCStatusView.as_view(), name="account-kyc-status"),
]