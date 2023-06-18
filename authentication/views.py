from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import GenerateOTPSerializer, OTPLoginSerializer, EmailSerializer
from .models import Email

User = get_user_model()


class EmailCreateAPIView(generics.CreateAPIView):
    serializer_class = EmailSerializer
    queryset = Email.objects.all()


class GenerateOTPView(generics.CreateAPIView):
    serializer_class = GenerateOTPSerializer
    queryset = User.objects.all()


class OTPLoginView(generics.GenericAPIView):
    serializer_class = OTPLoginSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]
        email = serializer.validated_data["email"]
        hotp = settings.PYOTP_HOTP

        email = User.objects.filter(email=email)
        if email.exists():
            user = email.first()
            if user.otp_secret_key is not None and hotp.verify(
                otp, user.otp_secret_key
            ):
                user.otp_secret_key = None
                user.is_active = True
                user.save()
                refresh = RefreshToken.for_user(user)
                data = {}
                data["refresh"] = str(refresh)
                data["access"] = str(refresh.access_token)
            else:
                raise serializers.ValidationError({"detail": "Invalid OTP."})

        else:
            raise serializers.ValidationError(
                {"detail": "Account with this email does not exists."}
            )

        return Response(data, status=status.HTTP_200_OK)
