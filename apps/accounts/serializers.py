"""
accounts/serializers.py

Serializers for authentication, account management, and contact inquiry endpoints.
"""

from rest_framework import serializers
from apps.common.validators import validate_mobile_number, validate_password_strength
from apps.accounts.models import User, OTPPurpose, ContactInquiry


class GuestRegistrationSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/register/"""

    full_name = serializers.CharField(max_length=150)
    mobile_number = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate_mobile_number(self, value):
        mobile = validate_mobile_number(value)
        if User.objects.filter(mobile_number=mobile).exists():
            raise serializers.ValidationError("An account with this mobile number already exists.")
        return mobile

    def validate_email(self, value):
        if value and value.strip():
            if User.objects.filter(email=value.strip()).exists():
                raise serializers.ValidationError("An account with this email already exists.")
            return value.strip()
        return None

    def validate(self, attrs):
        confirm = attrs.pop("confirm_password", None)
        if confirm and confirm != attrs["password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password_strength(attrs["password"])
        return attrs


class OTPRequestSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/otp/request/"""

    mobile_number = serializers.CharField(max_length=15)
    purpose = serializers.ChoiceField(choices=OTPPurpose.choices)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)


class OTPVerifySerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/otp/verify/"""

    mobile_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=4)
    purpose = serializers.ChoiceField(choices=OTPPurpose.choices)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)


class LoginSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/login/"""

    mobile_number = serializers.CharField(required=False, help_text="Mobile number (+91...)")
    identifier = serializers.CharField(required=False, help_text="Mobile number (+91...) or email address.")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        mobile = attrs.get("mobile_number") or attrs.get("identifier")
        if not mobile:
            raise serializers.ValidationError("Mobile number or identifier is required.")
        attrs["mobile_number"] = mobile
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/token/refresh/"""

    refresh = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/password/reset/request/"""

    mobile_number = serializers.CharField(max_length=15)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/password/reset/confirm/"""

    mobile_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6, min_length=4)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password_strength(attrs["new_password"])
        attrs.pop("confirm_password")
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Input validation for POST /api/v1/auth/password/change/"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password_strength(attrs["new_password"])
        attrs.pop("confirm_password")
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Output serializer for GET /api/v1/auth/me/"""

    public_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = [
            "public_id",
            "full_name",
            "mobile_number",
            "email",
            "account_type",
            "is_mobile_verified",
            "is_email_verified",
            "created_at",
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Input serializer for PATCH /api/v1/auth/me/"""

    class Meta:
        model = User
        fields = ["full_name", "email"]

    def validate_email(self, value):
        request = self.context.get("request")
        if value and User.objects.filter(email=value).exclude(pk=request.user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class ContactInquirySerializer(serializers.ModelSerializer):
    """Serializer for public contact inquiries"""

    class Meta:
        model = ContactInquiry
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "business_type",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class OAuthGoogleSerializer(serializers.Serializer):
    """Input for POST /api/v1/accounts/oauth/google/"""
    code = serializers.CharField(help_text="Google OAuth authorization code.")


class OAuthMicrosoftSerializer(serializers.Serializer):
    """Input for POST /api/v1/accounts/oauth/microsoft/"""
    code = serializers.CharField(help_text="Microsoft OAuth authorization code.")
