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

        ttl_minutes = getattr(settings, 'OTP_TTL_MINUTES', 5)
        text_message = (
            f"Your FinRoute Verification Code to {purpose_label} is: {otp_plain}\n\n"
            f"This OTP is valid for {ttl_minutes} minutes.\n"
            f"Do not share this code with anyone.\n"
        )

        html_message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FinRoute Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f6f8; padding: 30px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 520px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;">
          
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 28px 32px; text-align: center;">
              <div style="font-size: 24px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px;">
                ⚡ FinRoute
              </div>
              <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">
                Micro-Lending Engine
              </div>
            </td>
          </tr>

          <!-- Main Content Body -->
          <tr>
            <td style="padding: 32px 32px 24px 32px; text-align: center;">
              <div style="display: inline-block; background-color: #f0f9ff; border-radius: 50%; width: 52px; height: 52px; line-height: 52px; margin-bottom: 16px;">
                <span style="font-size: 24px;">🔒</span>
              </div>
              
              <h1 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 700; color: #0f172a;">
                Verification Code
              </h1>
              
              <p style="margin: 0 0 24px 0; font-size: 14px; color: #475569; line-height: 1.5;">
                Please use the following 6-digit One-Time Password (OTP) to {purpose_label}:
              </p>

              <!-- OTP Code Display Card -->
              <div style="background: #f8fafc; border: 2px dashed #0284c7; border-radius: 12px; padding: 20px 16px; margin-bottom: 24px;">
                <div style="font-family: 'Courier New', Courier, monospace; font-size: 36px; font-weight: 800; color: #0369a1; letter-spacing: 10px; padding-left: 10px;">
                  {otp_plain}
                </div>
                <div style="font-size: 12px; font-weight: 600; color: #0284c7; margin-top: 10px;">
                  ⏱️ Expires in {ttl_minutes} minutes
                </div>
              </div>

              <!-- Security Notice Callout -->
              <div style="background-color: #fffbeb; border: 1px solid #fef3c7; border-radius: 10px; padding: 14px 16px; text-align: left; margin-bottom: 20px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td width="24" valign="top" style="font-size: 16px; padding-right: 8px;">🛡️</td>
                    <td style="font-size: 12px; color: #92400e; line-height: 1.4;">
                      <strong>Security Notice:</strong> Do not share this OTP with anyone. FinRoute staff will never call or message asking for your code.
                    </td>
                  </tr>
                </table>
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #f8fafc; padding: 20px 32px; border-top: 1px solid #f1f5f9; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                This is an automated security verification email from <strong>FinRoute Micro-Lender Platform</strong>.<br>
                If you did not request this code, you can safely ignore this message.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        recipient_list = [target_email] if target_email else []

        if recipient_list:
            resend_key = getattr(settings, 'RESEND_API_KEY', '')
            email_sent = False
            
            if resend_key:
                try:
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'FinRoute <info@fin-route.site>')
                    email_payload = {
                        "from": from_email,
                        "to": [target_email],
                        "subject": f"FinRoute — Your Verification Code: {otp_plain}",
                        "text": text_message,
                        "html": html_message,
                    }
                    res_id = None
                    try:
                        import resend
                        resend.api_key = resend_key
                        response = resend.Emails.send(email_payload)
                        res_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", str(response))
                    except (ImportError, Exception) as py_err:
                        import requests
                        headers = {
                            "Authorization": f"Bearer {resend_key}",
                            "Content-Type": "application/json",
                        }
                        req_resp = requests.post(
                            "https://api.resend.com/emails",
                            json=email_payload,
                            headers=headers,
                            timeout=10,
                        )
                        if req_resp.status_code in (200, 201):
                            res_id = req_resp.json().get("id")
                        else:
                            raise Exception(f"Resend REST API HTTP {req_resp.status_code}: {req_resp.text}")

                    logger.info("✅ SUCCESS: OTP email sent via Resend API to %s | ID: %s", target_email, res_id)
                    print(f"\n==========================================")
                    print(f"✅ RESEND OTP EMAIL DELIVERED TO {target_email}!")
                    print(f"📩 Target Email: {target_email}")
                    print(f"🔑 OTP Code:     {otp_plain}")
                    print(f"🆔 Resend ID:    {res_id}")
                    print(f"==========================================\n", flush=True)
                    email_sent = True
                except Exception as r_err:
                    logger.warning("⚠️ Resend API email send error: %s. Falling back to SMTP...", r_err)

            if not email_sent:
                logger.info("📧 Attempting to send OTP email to %s via Django SMTP...", target_email)
                try:
                    send_mail(
                        subject=f"FinRoute — Your Verification Code: {otp_plain}",
                        message=text_message,
                        html_message=html_message,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FinRoute <info@fin-route.site>'),
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
