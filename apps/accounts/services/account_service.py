"""
accounts/services/account_service.py

AccountService handles user account lifecycle operations:
- Guest registration (atomic: User + GuestWorkspace + UserConsent)
- Profile retrieval and update
- Password change
- Account deactivation/reactivation
"""

import logging
from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import BusinessRuleException, DuplicateEntryException
from apps.common.validators import validate_mobile_number
from apps.accounts.models import User, AccountType, ConsentType, UserConsent
from apps.accounts.services.otp_service import OTPService
from apps.accounts.models import OTPPurpose

logger = logging.getLogger(__name__)


class AccountService:
    """
    Manages user account lifecycle.

    Critical rule: register_guest() must be atomic.
    If GuestWorkspace creation fails, the User must NOT be persisted.
    """

    @staticmethod
    @transaction.atomic
    def register_guest(validated_data: dict, ip: str = "", user_agent: str = "") -> User:
        """
        Register a new Guest Workspace user.

        Atomic transaction ensures:
        - User is created
        - GuestWorkspace is created (via GuestWorkspaceService)
        - UserConsent records are written
        - OTP is generated and sent

        If ANY step fails, the entire transaction rolls back.

        Args:
            validated_data: Validated data from GuestRegistrationSerializer.
            ip: Client IP address for consent audit.
            user_agent: Client User-Agent for consent audit.

        Returns:
            Newly created User instance.

        Raises:
            DuplicateEntryException if mobile already registered.
            BusinessRuleException for other failures.
        """
        mobile_number = validated_data["mobile_number"]
        password = validated_data["password"]
        full_name = validated_data["full_name"]
        email = validated_data.get("email")

        # Check uniqueness before creation
        if User.objects.filter(mobile_number=mobile_number).exists():
            raise DuplicateEntryException(
                "An account with this mobile number already exists."
            )

        # Create user account
        user = User.objects.create_user(
            mobile_number=mobile_number,
            password=password,
            full_name=full_name,
            email=email,
            account_type=AccountType.GUEST,
        )

        # Create Guest Workspace (GuestWorkspaceService owns this logic)
        from apps.guest_workspace.services.workspace_service import GuestWorkspaceService
        GuestWorkspaceService.create_default_workspace(owner=user)

        # Record consent records (TERMS_OF_SERVICE + PRIVACY_POLICY)
        AccountService._record_registration_consents(user, ip, user_agent)

        # Generate and send OTP for mobile verification
        otp_plain = OTPService.generate_and_store_otp(
            mobile_number=mobile_number,
            purpose=OTPPurpose.REGISTRATION,
            user=user,
        )
        OTPService.send_otp(mobile_number, otp_plain, OTPPurpose.REGISTRATION, recipient_email=email)

        logger.info("Guest user registered: mobile=%s", mobile_number)
        return user

    @staticmethod
    @transaction.atomic
    def verify_registration_otp(mobile_number: str, otp_plain: str) -> User:
        """
        Verify the registration OTP and activate the user's mobile number.

        Called from OTPVerifyAPIView after user submits OTP.

        Returns:
            Updated User instance with is_mobile_verified=True.
        """
        otp_record = OTPService.verify_otp(
            mobile_number=mobile_number,
            otp_plain=otp_plain,
            purpose=OTPPurpose.REGISTRATION,
        )

        # Mark mobile as verified
        user = User.objects.get(mobile_number=mobile_number)
        user.is_mobile_verified = True
        user.save(update_fields=["is_mobile_verified", "updated_at"])

        # Update OTP record to link to user
        if not otp_record.user:
            otp_record.user = user
            otp_record.save(update_fields=["user"])

        logger.info("Mobile verified for user=%s", mobile_number)
        return user

    @staticmethod
    def get_profile(user: User) -> dict:
        """Return the authenticated user's profile data."""
        return {
            "public_id": str(user.public_id),
            "full_name": user.full_name,
            "mobile_number": user.mobile_number,
            "email": user.email,
            "city": getattr(user, "city", "") or "",
            "state": getattr(user, "state", "") or "",
            "employee_id": getattr(user, "employee_id", "") or "",
            "account_type": user.account_type,
            "is_mobile_verified": user.is_mobile_verified,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at.isoformat(),
        }

    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        """
        Update editable profile fields.
        Mobile number and account_type changes are handled by separate flows.
        """
        allowed_fields = ["full_name", "email", "city", "state", "employee_id"]
        update_fields = ["updated_at"]

        for field in allowed_fields:
            if field in validated_data and hasattr(user, field):
                setattr(user, field, validated_data[field])
                update_fields.append(field)

        user.updated_at = timezone.now()
        user.save(update_fields=update_fields)

        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType
        AuditLogService.log_action(
            user=user,
            action=ActionType.UPDATE,
            target_model="User",
            target_id=str(user.public_id),
            description="Updated personal profile details",
        )

        logger.info("Profile updated for user=%s", user.mobile_number)
        return user

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> None:
        """
        Change a user's password after verifying the current password.

        Raises:
            BusinessRuleException if current password is wrong.
        """
        if not user.check_password(current_password):
            raise BusinessRuleException("Current password is incorrect.")

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType
        AuditLogService.log_action(
            user=user,
            action=ActionType.UPDATE,
            target_model="User",
            target_id=str(user.public_id),
            description="Updated account password",
        )

        logger.info("Password changed for user=%s", user.mobile_number)

    @staticmethod
    def _record_registration_consents(user: User, ip: str, user_agent: str) -> None:
        """Create ToS and Privacy Policy consent records during registration."""
        consent_records = [
            UserConsent(
                user=user,
                consent_type=ConsentType.TERMS_OF_SERVICE,
                version="v1.0",
                is_agreed=True,
                ip_address=ip or None,
                user_agent=user_agent,
            ),
            UserConsent(
                user=user,
                consent_type=ConsentType.PRIVACY_POLICY,
                version="v1.0",
                is_agreed=True,
                ip_address=ip or None,
                user_agent=user_agent,
            ),
        ]
        UserConsent.objects.bulk_create(consent_records)
