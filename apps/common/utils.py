"""
common/utils.py

Utility functions shared across all service classes.
"""

import hashlib
import secrets
import string
from datetime import date, timedelta
from django.conf import settings


def generate_otp(length: int = 6) -> str:
    """
    Generate a cryptographically secure numeric OTP.
    Uses secrets module for security — never use random.randint for OTPs.

    Args:
        length: Number of digits (default 6).

    Returns:
        Numeric OTP string.
    """
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


def hash_otp(otp_plain: str) -> str:
    """
    Hash an OTP using SHA-256 combined with a secret salt.
    The plain OTP is never stored — only the hash is persisted.

    Args:
        otp_plain: The plain text OTP generated.

    Returns:
        Hex-encoded SHA-256 hash of (otp + salt).
    """
    salt = getattr(settings, "OTP_SECRET_SALT", "default-dev-salt")
    payload = f"{otp_plain}{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_otp_hash(otp_plain: str, stored_hash: str) -> bool:
    """
    Verify an OTP against its stored hash using constant-time comparison.

    Args:
        otp_plain: The OTP provided by the user.
        stored_hash: The hash stored in the database.

    Returns:
        True if the OTP matches the stored hash.
    """
    return secrets.compare_digest(hash_otp(otp_plain), stored_hash)


def generate_customer_code(workspace_id: int, count: int) -> str:
    """
    Generate a unique customer code for a workspace.
    Format: FR{workspace_id:03d}{sequence:04d}
    Example: FR001-0042 for workspace 1, customer 42.

    Args:
        workspace_id: The workspace's internal ID.
        count: The next sequential customer count for this workspace.

    Returns:
        Formatted customer code string.
    """
    return f"FR{workspace_id:03d}{count:04d}"


def generate_receipt_number(workspace_id: int, date_val: date) -> str:
    """
    Generate a receipt number for a collection entry.
    Format: RCP-YYYYMMDD-XXXXXX (random 6-digit suffix).

    Args:
        workspace_id: The workspace ID prefix.
        date_val: The collection date.

    Returns:
        Receipt number string.
    """
    suffix = "".join(secrets.choice(string.digits) for _ in range(6))
    return f"RCP-{date_val.strftime('%Y%m%d')}-{workspace_id:03d}-{suffix}"


def get_week_date_range(reference_date: date = None):
    """
    Get the start and end dates of the ISO week containing the reference date.

    Args:
        reference_date: Date to use (defaults to today).

    Returns:
        Tuple (week_start: date, week_end: date)
    """
    if reference_date is None:
        reference_date = date.today()
    # ISO week starts on Monday
    week_start = reference_date - timedelta(days=reference_date.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_client_ip(request) -> str:
    """Extract the real client IP address from a Django request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_user_agent(request) -> str:
    """Extract the User-Agent header from a Django request."""
    return request.META.get("HTTP_USER_AGENT", "")
