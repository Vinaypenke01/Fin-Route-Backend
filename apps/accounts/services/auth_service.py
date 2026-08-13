"""
accounts/services/auth_service.py

AuthService handles authentication business logic:
- Login with mobile + password
- JWT token generation
- Logout and token blacklisting
- Password reset & change password workflows
- Account access validation
"""

import logging
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.common.exceptions import (
    AccountInactiveException,
    BusinessRuleException,
)
from apps.accounts.models import User, LoginHistory, LoginStatus, UserSession

logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles all authentication operations.
    """

    @classmethod
    def login_with_password(cls, identifier: str = "", password: str = "", ip: str = "", user_agent: str = "", **kwargs):
        from apps.common.validators import validate_mobile_number
        from django.db.models import Q

        raw_identifier = (identifier or kwargs.get("mobile_number") or "").strip()

        user = None
        if "@" in raw_identifier:
            user = User.objects.filter(email__iexact=raw_identifier, is_active=True).first()
        else:
            try:
                normalized = validate_mobile_number(raw_identifier)
            except Exception:
                normalized = raw_identifier

            cleaned_digits = "".join(filter(str.isdigit, raw_identifier))

            user = User.objects.filter(
                Q(mobile_number=normalized) | Q(mobile_number=cleaned_digits) | Q(email__iexact=raw_identifier),
                is_active=True,
            ).first()

        if not user or not user.check_password(password):
            if user:
                cls._record_login_history(
                    user=user,
                    ip=ip,
                    user_agent=user_agent,
                    status=LoginStatus.FAILED,
                    reason="Invalid password",
                )
            raise BusinessRuleException("Invalid email address / mobile number or password.")

        token_data = cls.issue_tokens(user, ip=ip, user_agent=user_agent)
        return user, token_data

    @classmethod
    def issue_tokens(cls, user: User, ip: str = "", user_agent: str = "") -> dict:
        cls.validate_account_access(user)

        refresh = RefreshToken.for_user(user)
        refresh["account_type"] = user.account_type

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        jti = str(refresh["jti"])

        cls._create_or_update_session(user, jti, refresh, ip, user_agent)
        cls._record_login_history(
            user=user,
            ip=ip,
            user_agent=user_agent,
            status=LoginStatus.SUCCESS,
        )

        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType
        AuditLogService.log_action(
            user=user,
            action=ActionType.LOGIN,
            target_model="User",
            target_id=str(user.public_id),
            description=f"User logged in from {user_agent or 'web browser'}",
            ip_address=ip,
            user_agent=user_agent,
        )

        User.objects.filter(pk=user.pk).update(last_login=timezone.now())

        workspace_data = cls._get_workspace_summary(user)

        logger.info("Issued tokens for user=%s", user.mobile_number)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "public_id": str(user.public_id),
                "full_name": user.full_name,
                "mobile_number": user.mobile_number,
                "account_type": user.account_type,
                "is_mobile_verified": user.is_mobile_verified,
            },
            "workspace": workspace_data,
        }

    @classmethod
    def logout(cls, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            jti = str(token["jti"])
            token.blacklist()
            UserSession.objects.filter(refresh_token_jti=jti).update(is_active=False)
        except TokenError as exc:
            raise BusinessRuleException(f"Logout failed: {exc}")

    @classmethod
    def validate_account_access(cls, user: User) -> None:
        if not user.is_active:
            raise AccountInactiveException()

    @classmethod
    def reset_password(cls, mobile_number: str, otp: str, new_password: str) -> None:
        from apps.common.validators import validate_mobile_number
        from apps.accounts.models import OTPVerification, OTPPurpose
        from apps.accounts.services.otp_service import OTPService

        try:
            normalized = validate_mobile_number(mobile_number)
        except Exception:
            normalized = mobile_number

        user = User.objects.filter(mobile_number=normalized, is_active=True).first()
        if not user:
            raise BusinessRuleException("Account not found.")

        # Verify OTP record exists and is verified
        otp_record = (
            OTPVerification.objects.filter(
                mobile_number=normalized,
                purpose=OTPPurpose.PASSWORD_RESET,
            )
            .order_by("-created_at")
            .first()
        )
        if not otp_record:
            raise BusinessRuleException("No active reset request found. Please request a new OTP.")

        if not otp_record.is_verified:
            OTPService.verify_otp(mobile_number=normalized, otp_plain=otp, purpose=OTPPurpose.PASSWORD_RESET)

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        logger.info("Password reset for user=%s", mobile_number)

    @classmethod
    def change_password(cls, user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise BusinessRuleException("Incorrect old password.")
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

    @classmethod
    def _create_or_update_session(
        cls,
        user: User,
        jti: str,
        refresh_token,
        ip: str,
        user_agent: str,
    ) -> None:
        from django.conf import settings
        from datetime import timedelta

        expires_at = timezone.now() + settings.SIMPLE_JWT.get(
            "REFRESH_TOKEN_LIFETIME", timedelta(days=7)
        )

        UserSession.objects.create(
            user=user,
            refresh_token_jti=jti,
            ip_address=ip or None,
            user_agent=user_agent or "",
            expires_at=expires_at,
            is_active=True,
        )

    @classmethod
    def _record_login_history(
        cls,
        user: User,
        ip: str,
        user_agent: str,
        status: str,
        reason: str = "",
    ) -> None:
        LoginHistory.objects.create(
            user=user,
            login_status=status,
            failure_reason=reason,
            ip_address=ip or None,
            user_agent=user_agent or "",
        )

    @classmethod
    def _get_workspace_summary(cls, user: User) -> dict:
        try:
            from apps.guest_workspace.models import GuestWorkspace
            workspace = GuestWorkspace.objects.get(owner=user)
            return {
                "public_id": str(workspace.public_id),
                "name": workspace.name,
                "plan": workspace.subscription_plan,
                "status": workspace.status,
            }
        except Exception:
            return None
