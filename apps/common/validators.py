"""
common/validators.py

Reusable field validators shared across all serializers.
"""

import re
from django.core.exceptions import ValidationError


def validate_mobile_number(value: str) -> str:
    """
    Validate and normalize an Indian mobile number.

    Accepts formats:
    - +919876543210
    - 9876543210
    - 09876543210

    Returns the normalized form: +91XXXXXXXXXX
    Raises ValidationError if invalid.
    """
    if not value:
        raise ValidationError("Mobile number is required.")

    # Remove all whitespace and dashes
    cleaned = re.sub(r"[\s\-\(\)]", "", str(value))

    # Normalize +91 prefix
    if cleaned.startswith("+91"):
        number = cleaned[3:]
    elif cleaned.startswith("91") and len(cleaned) == 12:
        number = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        number = cleaned[1:]
    else:
        number = cleaned

    # Validate: must be exactly 10 digits, starting with 6-9
    if not re.match(r"^[6-9]\d{9}$", number):
        raise ValidationError(
            f"'{value}' is not a valid Indian mobile number. "
            "It must be a 10-digit number starting with 6-9."
        )

    return f"+91{number}"


def validate_positive_amount(value) -> None:
    """Validates that a monetary amount is a positive number."""
    if value is not None and float(value) < 0:
        raise ValidationError("Amount must be a positive number.")


def validate_non_negative_amount(value) -> None:
    """Validates that a monetary amount is zero or positive."""
    if value is not None and float(value) < 0:
        raise ValidationError("Amount cannot be negative.")


def validate_future_date(value) -> None:
    """Validates that a date is not in the past (for use with loan start dates, etc.)."""
    from datetime import date
    if value and value < date.today():
        raise ValidationError("Date cannot be in the past.")


def validate_pin_code(value: str) -> None:
    """Validates a 6-digit Indian PIN code."""
    if not re.match(r"^\d{6}$", str(value)):
        raise ValidationError(f"'{value}' is not a valid 6-digit PIN code.")


def validate_password_strength(value: str) -> None:
    """
    Validates basic password strength rules:
    - Minimum 8 characters
    - Cannot be entirely numeric
    """
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if value.isdigit():
        raise ValidationError("Password cannot be entirely numeric.")
