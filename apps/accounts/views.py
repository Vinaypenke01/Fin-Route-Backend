"""
accounts/views.py

Authentication, account management, and contact inquiry views.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_spectacular.utils import extend_schema

from apps.common.responses import success_response, created_response, error_response
from apps.common.utils import get_client_ip, get_user_agent
from apps.accounts.serializers import (
    GuestRegistrationSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
    ContactInquirySerializer,
)
from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.account_service import AccountService
from apps.accounts.services.otp_service import OTPService
from apps.accounts.models import OTPPurpose, ContactInquiry

logger = logging.getLogger(__name__)


# ─── Custom Throttle Classes ─────────────────────────────────────────────────

class LoginThrottle(AnonRateThrottle):
    rate = "10/minute"
    scope = "auth_login"


class OTPThrottle(AnonRateThrottle):
    rate = "5/minute"
    scope = "auth_otp"


# ─── Registration ─────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """POST /api/v1/auth/register/ — Register Guest Workspace"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]
    serializer_class = GuestRegistrationSerializer

    @extend_schema(request=GuestRegistrationSerializer, responses={201: GuestRegistrationSerializer})
    def post(self, request):
        try:
            serializer = GuestRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message="Validation failed.", errors=serializer.errors)

            user = AccountService.register_guest(
                validated_data=serializer.validated_data,
                ip=get_client_ip(request),
                user_agent=get_user_agent(request),
            )

            return created_response(
                data={"mobile_number": user.mobile_number, "full_name": user.full_name, "next_step": "verify_otp"},
                message="Registration successful. Please verify your mobile number with the OTP sent.",
            )
        except Exception as e:
            logger.error("Registration error: %s", e, exc_info=True)
            return error_response(message=getattr(e, "detail", str(e)) or "Registration failed. Please try again.")


# ─── OTP Operations ──────────────────────────────────────────────────────────

class OTPRequestView(APIView):
    """POST /api/v1/auth/otp/request/ — Request a new OTP"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]
    serializer_class = OTPRequestSerializer

    @extend_schema(request=OTPRequestSerializer)
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        mobile = serializer.validated_data["mobile_number"]
        purpose = serializer.validated_data["purpose"]
        otp_plain = OTPService.generate_and_store_otp(mobile_number=mobile, purpose=purpose)
        OTPService.send_otp(mobile_number=mobile, otp_plain=otp_plain, purpose=purpose)

        return success_response(message="OTP sent successfully.")


class OTPVerifyView(APIView):
    """POST /api/v1/auth/otp/verify/ — Verify OTP"""
    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

    @extend_schema(request=OTPVerifySerializer)
    def post(self, request):
        try:
            serializer = OTPVerifySerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(errors=serializer.errors)

            mobile = serializer.validated_data["mobile_number"]
            otp = serializer.validated_data["otp"]
            purpose = serializer.validated_data["purpose"]

            otp_record = OTPService.verify_otp(mobile_number=mobile, otp_plain=otp, purpose=purpose)
            
            from apps.accounts.models import User
            user = otp_record.user or User.objects.filter(mobile_number=mobile).first()

            if user:
                user.is_mobile_verified = True
                user.save(update_fields=["is_mobile_verified", "updated_at"])

            token_data = None
            if user:
                token_data = AuthService.issue_tokens(user, get_client_ip(request), get_user_agent(request))

            return success_response(data=token_data, message="OTP verified successfully.")
        except Exception as e:
            logger.error("OTP verification error: %s", e)
            return error_response(message=getattr(e, "detail", str(e)) or "Invalid or expired OTP.")


class OTPResendView(APIView):
    """POST /api/v1/auth/otp/resend/ — Resend OTP"""
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        mobile = request.data.get("mobile_number")
        purpose = request.data.get("purpose", OTPPurpose.LOGIN)
        if not mobile:
            return error_response("Mobile number is required.")

        otp_plain = OTPService.generate_and_store_otp(mobile_number=mobile, purpose=purpose)
        OTPService.send_otp(mobile_number=mobile, otp_plain=otp_plain, purpose=purpose)

        return success_response(message="OTP resent successfully.")


# ─── Login & Logout ──────────────────────────────────────────────────────────

class LoginView(APIView):
    """POST /api/v1/auth/login/ — Mobile + Password login"""
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        mobile = serializer.validated_data["mobile_number"]
        password = serializer.validated_data["password"]

        user, token_data = AuthService.login_with_password(
            mobile_number=mobile,
            password=password,
            ip=get_client_ip(request),
            user_agent=get_user_agent(request),
        )

        return success_response(data=token_data, message="Login successful.")


class LogoutView(APIView):
    """POST /api/v1/auth/logout/ — Blacklist refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            AuthService.logout(refresh_token)
        return success_response(message="Logged out successfully.")


# ─── Password Reset ──────────────────────────────────────────────────────────

class ForgotPasswordView(APIView):
    """POST /api/v1/auth/password/forgot/"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        mobile = serializer.validated_data["mobile_number"]
        otp_plain = OTPService.generate_and_store_otp(mobile_number=mobile, purpose=OTPPurpose.PASSWORD_RESET)
        OTPService.send_otp(mobile_number=mobile, otp_plain=otp_plain, purpose=OTPPurpose.PASSWORD_RESET)

        return success_response(message="Password reset OTP sent.")


class ResetPasswordView(APIView):
    """POST /api/v1/auth/password/reset/"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        AuthService.reset_password(
            mobile_number=serializer.validated_data["mobile_number"],
            otp=serializer.validated_data["otp"],
            new_password=serializer.validated_data["new_password"],
        )

        return success_response(message="Password reset successfully.")


class ChangePasswordView(APIView):
    """POST /api/v1/auth/password/change/"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        AuthService.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )

        return success_response(message="Password changed successfully.")


# ─── User Profile ─────────────────────────────────────────────────────────────

class MeView(APIView):
    """GET/PATCH /api/v1/auth/me/ — User Profile"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(responses={200: UserProfileSerializer})
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)

    @extend_schema(request=UserProfileUpdateSerializer, responses={200: UserProfileSerializer})
    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        updated_user = AccountService.update_profile(request.user, serializer.validated_data)
        output = UserProfileSerializer(updated_user)
        return success_response(data=output.data, message="Profile updated successfully.")


# ─── Contact Inquiry ──────────────────────────────────────────────────────────

class ContactInquiryCreateView(APIView):
    """POST /api/v1/accounts/contact-us/ — Public demo/sales inquiry"""
    permission_classes = [AllowAny]
    serializer_class = ContactInquirySerializer

    @extend_schema(summary="Submit a sales/demo contact inquiry", request=ContactInquirySerializer)
    def post(self, request):
        serializer = ContactInquirySerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        inquiry = serializer.save()
        return created_response(
            data=ContactInquirySerializer(inquiry).data,
            message="Thank you! Your inquiry has been received. Our sales team will get in touch shortly.",
        )


# ─── OAuth Stubs ──────────────────────────────────────────────────────────────

class OAuthGoogleView(APIView):
    """POST /api/v1/accounts/oauth/google/"""
    permission_classes = [AllowAny]

    def post(self, request):
        return error_response(message="Google OAuth coming soon.", http_status=501)


class OAuthMicrosoftView(APIView):
    """POST /api/v1/accounts/oauth/microsoft/"""
    permission_classes = [AllowAny]

    def post(self, request):
        return error_response(message="Microsoft OAuth coming soon.", http_status=501)
