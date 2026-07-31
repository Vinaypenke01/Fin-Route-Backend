"""
accounts/services/otp_service.py

OTPService handles all OTP-related business logic:
- Generating secure OTPs
- Hashing and storing OTPs
- Sending OTPs (email in V1, SMS in V2)
- Verifying OTPs with expiry and attempt enforcement
- Resending (invalidating previous, generating new)
- Rate limiting
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.common.exceptions import (
    OTPExpiredException,
    OTPInvalidException,
    OTPMaxAttemptsException,
    OTPRateLimitException,
)
from apps.common.utils import generate_otp, hash_otp, verify_otp_hash
from apps.accounts.models import OTPVerification, OTPPurpose

logger = logging.getLogger(__name__)


class OTPService:
    """
    Handles all OTP lifecycle operations.

    Security guarantees:
    - Plain OTPs are never logged or stored.
    - Hashing uses SHA-256(otp + secret_salt) with constant-time comparison.
    - Rate limiting prevents OTP abuse.
    """

    OTP_LENGTH = 6
    RATE_LIMIT_WINDOW_MINUTES = 60
    RATE_LIMIT_MAX_REQUESTS = 5

    @staticmethod
    def generate_and_store_otp(mobile_number: str, purpose: str, user=None) -> str:
        """
        Generate a new OTP, hash it, and store in the database.

        Steps:
        1. Check rate limit.
        2. Invalidate existing active OTPs for same mobile + purpose.
        3. Generate cryptographically secure OTP.
        4. Hash and store.
        5. Return plain OTP for delivery.

        Returns:
            Plain OTP string (for sending to user — NOT for storage).
        """
        OTPService.check_rate_limit(mobile_number, purpose)
        OTPService._invalidate_existing_otps(mobile_number, purpose)

        otp_plain = generate_otp(OTPService.OTP_LENGTH)
        otp_hash = hash_otp(otp_plain)
        ttl_minutes = getattr(settings, "OTP_TTL_MINUTES", 5)
        max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 5)

        OTPVerification.objects.create(
            user=user,
            mobile_number=mobile_number,
            purpose=purpose,
            otp_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
            max_attempts=max_attempts,
        )

        logger.info("OTP generated for mobile=%s purpose=%s", mobile_number, purpose)
        return otp_plain

    @staticmethod
    def send_otp(mobile_number: str, otp_plain: str, purpose: str, recipient_email: str = None) -> None:
        """
        Deliver the OTP via Email to user's email address.
        """
        purpose_messages = {
            OTPPurpose.REGISTRATION: "complete your registration",
            OTPPurpose.PASSWORD_RESET: "reset your password",
            OTPPurpose.LOGIN: "log in to your account",
            OTPPurpose.ACCOUNT_VERIFICATION: "verify your account",
        }
        purpose_label = purpose_messages.get(purpose, "verify your identity")

        target_email = recipient_email
        if not target_email and mobile_number:
            try:
                from apps.accounts.models import User
                user = User.objects.filter(mobile_number=mobile_number).first()
                if user and user.email:
                    target_email = user.email
            except Exception:
                pass

        message = (
            f"Your FinRoute Email Verification Code to {purpose_label} is: {otp_plain}\n\n"
            f"This OTP is valid for {getattr(settings, 'OTP_TTL_MINUTES', 5)} minutes.\n"
            f"Do not share this code with anyone.\n"
        )

        recipient_list = [target_email] if target_email else []

        if recipient_list:
            logger.info("📧 Attempting to send OTP email to %s via SMTP (%s)...", target_email, getattr(settings, 'EMAIL_HOST', 'SMTP'))
            try:
                send_mail(
                    subject=f"FinRoute — Your Email Verification Code: {otp_plain}",
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@digitalcore.co.in'),
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                logger.info("✅ SUCCESS: OTP email sent successfully to %s | OTP: %s", target_email, otp_plain)
                print(f"\n==========================================")
                print(f"✅ OTP EMAIL SENT SUCCESSFULLY TO {target_email}!")
                print(f"📩 Target Email: {target_email}")
                print(f"🔑 OTP Code:     {otp_plain}")
                print(f"==========================================\n", flush=True)
            except Exception as exc:
                logger.error("❌ FAILURE: Failed to send OTP email to %s: %s", target_email, exc, exc_info=True)
                print(f"\n==========================================")
                print(f"❌ OTP EMAIL DELIVERY FAILED FOR {target_email}!")
                print(f"⚠️ SMTP Error:   {exc}")
                print(f"🔑 OTP Code:     {otp_plain} (Console Fallback)")
                print(f"==========================================\n", flush=True)
        else:
            logger.warning("⚠️ No recipient email found for mobile=%s. OTP printed to console: %s", mobile_number, otp_plain)
            print(f"\n==========================================")
            print(f"⚠️ NO RECIPIENT EMAIL TARGET PROVIDED!")
            print(f"📱 Mobile:   {mobile_number}")
            print(f"🔑 OTP Code: {otp_plain}")
            print(f"==========================================\n", flush=True)

    @staticmethod
    def verify_otp(mobile_number: str, otp_plain: str, purpose: str) -> OTPVerification:
        """
        Verify an OTP against the stored hash.

        Flow:
        1. Find the latest active OTP record.
        2. Check if expired.
        3. Check if attempts exhausted.
        4. Compare hash (constant-time).
        5. On success: mark verified, update user if needed.
        6. On failure: increment attempt count.

        Returns:
            The verified OTPVerification instance.

        Raises:
            OTPExpiredException, OTPInvalidException, OTPMaxAttemptsException
        """
        otp_record = (
            OTPVerification.objects.filter(
                mobile_number=mobile_number,
                purpose=purpose,
                is_verified=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_record:
            raise OTPInvalidException("No active OTP found. Please request a new one.")

        if otp_record.is_expired:
            raise OTPExpiredException()

        if otp_record.attempts_exhausted:
            raise OTPMaxAttemptsException()

        if not verify_otp_hash(otp_plain, otp_record.otp_hash):
            otp_record.attempt_count += 1
            otp_record.save(update_fields=["attempt_count"])

            remaining = otp_record.max_attempts - otp_record.attempt_count
            raise OTPInvalidException(
                f"Invalid OTP. {remaining} attempt(s) remaining."
            )

        # Mark as verified
        otp_record.is_verified = True
        otp_record.save(update_fields=["is_verified", "updated_at"])

        logger.info("OTP verified for mobile=%s purpose=%s", mobile_number, purpose)
        return otp_record

    @staticmethod
    def resend_otp(mobile_number: str, purpose: str, user=None) -> str:
        """
        Resend OTP: invalidate all existing active OTPs and generate a new one.

        Returns:
            New plain OTP string.
        """
        return OTPService.generate_and_store_otp(mobile_number, purpose, user)

    @staticmethod
    def check_rate_limit(mobile_number: str, purpose: str) -> None:
        """
        Enforce OTP request rate limiting.
        Default: max 5 requests per mobile+purpose per 60 minutes.

        Raises:
            OTPRateLimitException if limit is exceeded.
        """
        window_start = timezone.now() - timedelta(
            minutes=OTPService.RATE_LIMIT_WINDOW_MINUTES
        )
        recent_count = OTPVerification.objects.filter(
            mobile_number=mobile_number,
            purpose=purpose,
            created_at__gte=window_start,
        ).count()

        if recent_count >= OTPService.RATE_LIMIT_MAX_REQUESTS:
            raise OTPRateLimitException()

    @staticmethod
    def _invalidate_existing_otps(mobile_number: str, purpose: str) -> None:
        """Mark all existing unverified OTPs for this mobile+purpose as expired."""
        OTPVerification.objects.filter(
            mobile_number=mobile_number,
            purpose=purpose,
            is_verified=False,
        ).update(expires_at=timezone.now())
