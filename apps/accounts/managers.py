"""
accounts/managers.py

Custom user manager for the User model.

Rules:
- Passwords must NEVER be set manually — always use set_password().
- Mobile numbers must be normalized before persistence.
- Email must be normalized (lowercased) when provided.
"""

import re
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model that uses mobile_number as the
    primary identifier instead of username.
    """

    @staticmethod
    def normalize_mobile_number(mobile: str) -> str:
        """
        Normalize a mobile number to the format: +91XXXXXXXXXX.
        Raises ValueError if the number is not valid.
        """
        if not mobile:
            raise ValueError("Mobile number is required.")

        cleaned = re.sub(r"[\s\-\(\)]", "", str(mobile))

        if cleaned.startswith("+91"):
            number = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            number = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            number = cleaned[1:]
        else:
            number = cleaned

        if not re.match(r"^[6-9]\d{9}$", number):
            raise ValueError(
                f"'{mobile}' is not a valid Indian mobile number."
            )

        return f"+91{number}"

    def create_user(self, mobile_number: str, password: str, full_name: str = "", **extra_fields):
        """
        Create and return a standard user account.
        """
        if not mobile_number:
            raise ValueError("Mobile number is required.")
        if not password:
            raise ValueError("Password is required.")

        mobile_number = self.normalize_mobile_number(mobile_number)

        if "email" in extra_fields and extra_fields["email"]:
            extra_fields["email"] = self.normalize_email(extra_fields["email"])

        user = self.model(
            mobile_number=mobile_number,
            full_name=full_name,
            **extra_fields,
        )
        user.set_password(password)  # Always use set_password — never raw assignment
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number: str, password: str, full_name: str = "Admin", **extra_fields):
        """
        Create and return a superuser (Super Admin) account.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_mobile_verified", True)
        extra_fields.setdefault("account_type", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(mobile_number, password, full_name, **extra_fields)
