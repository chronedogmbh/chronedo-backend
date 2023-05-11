import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework import serializers

User = get_user_model()


class GenerateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        hotp = settings.PYOTP_HOTP
        email = validated_data["email"]
        user, created = User.objects.get_or_create(email=email)
        user.otp_secret_key = random.randint(100000, 999999)
        user.save()
        otp = hotp.at(user.otp_secret_key)
        send_mail(
            "Email Verification for Chrono App",
            f"Your OTP for ChronoApp is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return user


class OTPLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    otp = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "otp"]
