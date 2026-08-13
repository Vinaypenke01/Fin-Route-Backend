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
            
            from apps.accounts.models import User, OTPPurpose
            user = otp_record.user or User.objects.filter(mobile_number=mobile).first()

            token_data = None
            if user and purpose != OTPPurpose.PASSWORD_RESET:
                user.is_mobile_verified = True
                user.save(update_fields=["is_mobile_verified", "updated_at"])
                token_data = AuthService.issue_tokens(user, get_client_ip(request), get_user_agent(request))

            return success_response(data=token_data or {"verified": True}, message="OTP verified successfully.")
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

        identifier = serializer.validated_data.get("identifier") or serializer.validated_data.get("mobile_number")
        password = serializer.validated_data["password"]

        user, token_data = AuthService.login_with_password(
            identifier=identifier,
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

    def post(self, request):
        raw_identifier = (request.data.get("email") or request.data.get("mobile_number") or request.data.get("identifier") or "").strip()
        if not raw_identifier:
            return error_response(message="Please enter your registered email address or mobile number.")

        from apps.accounts.models import User, OTPPurpose
        from django.db.models import Q
        
        user = User.objects.filter(
            Q(email__iexact=raw_identifier) | Q(mobile_number=raw_identifier),
            is_active=True,
        ).first()

        if not user:
            cleaned = "".join(filter(str.isdigit, raw_identifier))
            if cleaned:
                user = User.objects.filter(mobile_number=cleaned, is_active=True).first()

        if not user:
            return error_response(message="No active account found with that email address or mobile number.")

        target_email = user.email
        otp_plain = OTPService.generate_and_store_otp(
            mobile_number=user.mobile_number,
            purpose=OTPPurpose.PASSWORD_RESET,
            user=user,
        )
        OTPService.send_otp(
            mobile_number=user.mobile_number,
            otp_plain=otp_plain,
            purpose=OTPPurpose.PASSWORD_RESET,
            recipient_email=target_email,
        )

        masked_email = ""
        if target_email and "@" in target_email:
            parts = target_email.split("@")
            name = parts[0]
            masked_name = name[0] + "*" * max(len(name) - 2, 1) + (name[-1] if len(name) > 1 else "")
            masked_email = f"{masked_name}@{parts[1]}"

        msg = f"A 6-digit password reset OTP has been sent to your email ({masked_email})." if masked_email else "Password reset OTP sent to your registered email."
        return success_response(data={"mobile_number": user.mobile_number, "email": target_email}, message=msg)


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


class UserActivityView(APIView):
    """GET /api/v1/auth/me/activity/ — Fetch user's recent audit activities with filters & pagination"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.audit_logs.models import AuditLog
        from apps.audit_logs.serializers import AuditLogSerializer
        from django.db.models import Q

        queryset = AuditLog.objects.filter(user=request.user).order_by("-created_at")

        action = request.query_params.get("action")
        if action and action != "all":
            queryset = queryset.filter(action__iexact=action)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | Q(target_model__icontains=search)
            )

        date_str = request.query_params.get("date")
        if date_str:
            queryset = queryset.filter(created_at__date=date_str)

        day = request.query_params.get("day")
        if day and day != "all":
            day_map = {"monday": 2, "tuesday": 3, "wednesday": 4, "thursday": 5, "friday": 6, "saturday": 7, "sunday": 1}
            if day.lower() in day_map:
                queryset = queryset.filter(created_at__week_day=day_map[day.lower()])

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuditLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


# ─── Sessions & Devices ────────────────────────────────────────────────────────

class UserSessionListView(APIView):
    """GET /api/v1/auth/sessions/ — List all active sessions for current user with pagination"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.accounts.models import UserSession
        from apps.accounts.serializers import UserSessionSerializer
        from django.db.models import Q

        queryset = UserSession.objects.filter(user=request.user, is_active=True).order_by("-last_activity_at")

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(device_name__icontains=search) |
                Q(device_type__icontains=search) |
                Q(user_agent__icontains=search) |
                Q(ip_address__icontains=search)
            )

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserSessionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserSessionRevokeView(APIView):
    """DELETE /api/v1/auth/sessions/<int:session_id>/ — Revoke a specific session/device"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        from apps.accounts.models import UserSession
        from django.utils import timezone
        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType

        try:
            session = UserSession.objects.get(id=session_id, user=request.user)
            session.is_active = False
            session.revoked_at = timezone.now()
            session.save()

            AuditLogService.log_action(
                user=request.user,
                action=ActionType.LOGOUT,
                target_model="UserSession",
                target_id=str(session.id),
                description=f"Revoked device session: {session.device_name or session.user_agent[:30]}",
            )
            return success_response(message="Device session revoked successfully.")
        except UserSession.DoesNotExist:
            return error_response(message="Session not found.")


class UserSessionRevokeAllView(APIView):
    """POST /api/v1/auth/sessions/revoke-all/ — Revoke all other active sessions"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.accounts.models import UserSession
        from django.utils import timezone
        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType

        updated_count = UserSession.objects.filter(user=request.user, is_active=True).update(
            is_active=False,
            revoked_at=timezone.now(),
        )

        AuditLogService.log_action(
            user=request.user,
            action=ActionType.LOGOUT,
            target_model="UserSession",
            description=f"Signed out of all {updated_count} active sessions/devices",
        )

        return success_response(message=f"Successfully signed out of {updated_count} session(s).")


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
