"""
common/exceptions.py

Custom exception classes and the global DRF exception handler.

All business rule violations must be raised as specific exception types
so the handler can format them consistently with the standard response shape.
"""

import logging
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)


# ─── Custom Exception Classes ─────────────────────────────────────────────────

class BusinessRuleException(APIException):
    """Raised when a domain business rule is violated."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A business rule was violated."
    default_code = "business_rule_error"


class PlanLimitExceededException(APIException):
    """Raised when a Guest Workspace exceeds its Free/Premium plan limits."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Plan limit exceeded."
    default_code = "GUEST_PLAN_LIMIT_REACHED"

    def __init__(self, detail=None, usage=None, upgrade_url="/app/upgrade"):
        self.upgrade_url = upgrade_url
        self.usage = usage or {}
        super().__init__(detail=detail)


class OTPExpiredException(APIException):
    """Raised when the provided OTP has expired."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "OTP has expired. Please request a new one."
    default_code = "otp_expired"


class OTPInvalidException(APIException):
    """Raised when the provided OTP is incorrect."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid OTP provided."
    default_code = "otp_invalid"


class OTPMaxAttemptsException(APIException):
    """Raised when OTP verification attempts are exhausted."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Maximum OTP attempts reached. Please request a new OTP."
    default_code = "otp_max_attempts"


class OTPRateLimitException(APIException):
    """Raised when OTP request rate limit is hit."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Too many OTP requests. Please wait before requesting again."
    default_code = "otp_rate_limit"


class AccountInactiveException(APIException):
    """Raised when a deactivated account attempts to authenticate."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "This account has been deactivated. Please contact support."
    default_code = "account_inactive"


class DuplicateEntryException(APIException):
    """Raised when a unique constraint would be violated at the service layer."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A duplicate entry was detected."
    default_code = "duplicate_entry"


class WorkspaceNotFoundException(APIException):
    """Raised when a workspace cannot be found for the authenticated user."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Workspace not found."
    default_code = "workspace_not_found"


class WorkspaceSuspendedException(APIException):
    """Raised when a suspended workspace attempts an operation."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "This workspace has been suspended. Please contact support."
    default_code = "workspace_suspended"


class CustomerNotFoundException(APIException):
    """Raised when a requested customer is not found in the workspace."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Customer not found."
    default_code = "customer_not_found"


class CollectionNotFoundException(APIException):
    """Raised when a requested collection entry is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Collection entry not found."
    default_code = "collection_not_found"


class ExpenseNotFoundException(APIException):
    """Raised when a requested expense is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Expense not found."
    default_code = "expense_not_found"


# ─── Global Exception Handler ─────────────────────────────────────────────────

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that wraps all errors in the standard
    response envelope:
    {
        "success": false,
        "message": "...",
        "data": null,
        "errors": {...}
    }
    """
    # Convert raw ValueError into 400 Bad Request
    if isinstance(exc, ValueError):
        logger.warning("Validation ValueError: %s", exc)
        return Response(
            {
                "success": False,
                "message": str(exc),
                "data": None,
                "errors": {"mobile_number": [str(exc)]},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Call DRF's default exception handler
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code >= 500:
            logger.error("Server error: %s", exc, exc_info=True)

        errors = {}
        message = "An error occurred."

        if isinstance(exc.detail, dict):
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    errors[field] = [str(m) for m in messages]
                else:
                    errors[field] = str(messages)
            message = "Validation failed. Please check the submitted data."
        elif isinstance(exc.detail, list):
            message = " ".join([str(d) for d in exc.detail])
        else:
            message = str(exc.detail)

        payload = {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        }

        if isinstance(exc, PlanLimitExceededException):
            payload["error_code"] = exc.default_code
            payload["usage"] = exc.usage
            payload["upgrade_prompt"] = {
                "message": "Upgrade to Guest Premium for higher limits.",
                "upgrade_url": exc.upgrade_url,
            }

        response.data = payload

    else:
        logger.exception("Unhandled exception: %s", exc)
        response = Response(
            {
                "success": False,
                "message": "An internal server error occurred.",
                "data": None,
                "errors": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
