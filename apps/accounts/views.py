from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.permissions import IsNotReadOnlyAuditor
from apps.accounts.models import KYCProfile
from apps.accounts.serializers import (
    KYCProfileSerializer,
    KYCProfileSubmitSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "User registered successfully.",
                "user": response.data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsNotReadOnlyAuditor]

    def get_object(self):
        return self.request.user


class KYCProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "kyc_profile", None)

        if profile is None:
            return Response(
                {"detail": "KYC profile has not been submitted."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(KYCProfileSerializer(profile).data)

    def post(self, request):
        serializer = KYCProfileSubmitSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(
            {
                "message": "KYC profile submitted successfully.",
                "kyc_profile": KYCProfileSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        serializer = KYCProfileSubmitSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(
            {
                "message": "KYC profile updated successfully.",
                "kyc_profile": KYCProfileSerializer(profile).data,
            },
            status=status.HTTP_200_OK,
        )


class KYCStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "kyc_profile", None)

        if profile is None:
            return Response(
                {
                    "verification_status": "NOT_SUBMITTED",
                    "attempt_count": 0,
                }
            )

        return Response(
            {
                "verification_status": profile.verification_status,
                "attempt_count": profile.attempt_count,
                "verified_at": profile.verified_at,
            }
        )