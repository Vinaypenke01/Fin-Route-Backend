"""
accounts/urls/auth_urls.py — Authentication URL routes.
Mounted at: /api/v1/auth/
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import (
    RegisterView,
    OTPRequestView,
    OTPVerifyView,
    OTPResendView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    MeView,
    UserActivityView,
    UserSessionListView,
    UserSessionRevokeView,
    UserSessionRevokeAllView,
)

urlpatterns = [
    # Registration
    path("register/", RegisterView.as_view(), name="auth-register"),

    # OTP
    path("otp/request/", OTPRequestView.as_view(), name="auth-otp-request"),
    path("otp/verify/", OTPVerifyView.as_view(), name="auth-otp-verify"),
    path("otp/resend/", OTPResendView.as_view(), name="auth-otp-resend"),

    # Login / Logout / Token
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),

    # Password Management
    path("password/forgot/", ForgotPasswordView.as_view(), name="auth-password-forgot"),
    path("password/reset/", ResetPasswordView.as_view(), name="auth-password-reset"),
    path("password/change/", ChangePasswordView.as_view(), name="auth-password-change"),

    # Current User Profile & Activity Log
    path("me/", MeView.as_view(), name="auth-me"),
    path("me/activity/", UserActivityView.as_view(), name="auth-me-activity"),

    # Active Sessions & Device Management
    path("sessions/", UserSessionListView.as_view(), name="auth-sessions"),
    path("sessions/<int:session_id>/", UserSessionRevokeView.as_view(), name="auth-sessions-revoke"),
    path("sessions/revoke-all/", UserSessionRevokeAllView.as_view(), name="auth-sessions-revoke-all"),
]
