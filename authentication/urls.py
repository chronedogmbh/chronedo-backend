from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import EmailCreateAPIView

urlpatterns = [
    # path("generate-otp/", GenerateOTPView.as_view(), name="generate-otp"),
    # path("otp-login/", OTPLoginView.as_view(), name="otp-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("email/", EmailCreateAPIView.as_view(), name="email"),
]
