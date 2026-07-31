"""
accounts/models.py

User model, OTP verification, login history, session tracking, user consent, and contact inquiries.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel, BasePublicModel
from .managers import UserManager


# ─── Account Type Choices ─────────────────────────────────────────────────────

class AccountType(models.TextChoices):
    GUEST = "guest", "Guest"
    LENDER = "lender", "Lender"
    EMPLOYEE = "employee", "Employee"
    ADMIN = "admin", "Admin"


# ─── User Model ───────────────────────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):
    """
    Central identity model for every authenticated person on the platform.
    """

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        help_text="External-facing UUID. Safe to expose in APIs.",
    )

    # --- Login Credentials ---
    mobile_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        help_text="Primary login identifier. Stored in normalized format: +91XXXXXXXXXX.",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        help_text="Optional email. Can be used for notifications and future email login.",
    )

    # --- Profile ---
    full_name = models.CharField(
        max_length=150,
        help_text="User's display name.",
    )

    # --- Account Type ---
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.GUEST,
        db_index=True,
        help_text="Determines the user's platform role and capabilities.",
    )

    # --- Verification Status ---
    is_mobile_verified = models.BooleanField(
        default=False,
        help_text="Set to True after successful OTP verification.",
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Set to True after email link verification.",
    )

    # --- Account Status ---
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive users cannot authenticate.",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Grants access to Django admin interface.",
    )

    # --- Audit Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.mobile_number}) — {self.account_type}"


# ─── OTP Verification ─────────────────────────────────────────────────────────

class OTPPurpose(models.TextChoices):
    REGISTRATION = "registration", "Registration"
    LOGIN = "login", "Login"
    PASSWORD_RESET = "password_reset", "Password Reset"
    ACCOUNT_VERIFICATION = "account_verification", "Account Verification"


class OTPVerification(BaseModel):
    mobile_number = models.CharField(max_length=15, db_index=True)
    otp_hash = models.CharField(max_length=255)
    purpose = models.CharField(max_length=50, choices=OTPPurpose.choices)
    attempt_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="otps")

    class Meta:
        verbose_name = "OTP Verification"
        verbose_name_plural = "OTP Verifications"
        ordering = ["-created_at"]

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def attempts_exhausted(self) -> bool:
        return self.attempt_count >= self.max_attempts

    def __str__(self):
        return f"OTP({self.mobile_number} - {self.purpose})"


# ─── Login History & Session Management ──────────────────────────────────────

class LoginStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    BLOCKED = "blocked", "Blocked"


class LoginHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_history")
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    login_status = models.CharField(max_length=20, choices=LoginStatus.choices, default=LoginStatus.SUCCESS)
    failure_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "Login History"
        verbose_name_plural = "Login Histories"
        ordering = ["-login_at"]


class UserSession(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh_token_jti = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=200, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ["-created_at"]


# ─── User Consent ─────────────────────────────────────────────────────────────

class ConsentType(models.TextChoices):
    TERMS_OF_SERVICE = "terms_of_service", "Terms of Service"
    PRIVACY_POLICY = "privacy_policy", "Privacy Policy"
    CREDIT_REPORT_AUTHORIZATION = "credit_report_auth", "Credit Report Authorization"
    DATA_PROCESSING = "data_processing", "Data Processing Consent"


class UserConsent(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="consents",
    )
    consent_type = models.CharField(
        max_length=50,
        choices=ConsentType.choices,
    )
    version = models.CharField(max_length=20)
    is_agreed = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    accepted_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "User Consent"
        verbose_name_plural = "User Consents"
        ordering = ["-accepted_at"]


# ─── Public Contact Inquiries ──────────────────────────────────────────────────

class ContactInquiryStatus(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    CLOSED = "closed", "Closed"


class ContactInquiry(BaseModel):
    """
    Public sales/demo inquiries submitted via the public /contact page.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    business_type = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ContactInquiryStatus.choices,
        default=ContactInquiryStatus.NEW,
    )

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inquiry({self.first_name} {self.last_name} — {self.email})"
