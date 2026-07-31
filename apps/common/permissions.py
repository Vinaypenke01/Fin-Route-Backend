"""
common/permissions.py

Reusable DRF permission classes for the Finance ERP.
These are applied at the view level and must not contain business logic.
"""

from rest_framework.permissions import BasePermission


class IsGuestUser(BasePermission):
    """
    Allows access only to authenticated users with account_type = 'guest'.
    Used for all /api/v1/app/* endpoints.
    """
    message = "Access restricted to Guest Workspace accounts."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.account_type == "guest"
        )


class IsLenderUser(BasePermission):
    """
    Allows access only to authenticated users with account_type = 'lender'.
    Used for V2 /api/v1/erp/* endpoints.
    """
    message = "Access restricted to ERP Lender accounts."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.account_type == "lender"
        )


class IsEmployeeUser(BasePermission):
    """
    Allows access only to authenticated users with account_type = 'employee'.
    Used for V2 /api/v1/field/* endpoints.
    """
    message = "Access restricted to Employee (Field) accounts."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.account_type == "employee"
        )


class IsGuestOrLenderUser(BasePermission):
    """
    Allows access to authenticated users who are guests or lenders.
    Useful for shared endpoints accessible by both workspace types.
    """
    message = "Access restricted to Guest or Lender accounts."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.account_type in ("guest", "lender")
        )


class IsSuperAdmin(BasePermission):
    """
    Allows access to Super Admin accounts (is_superuser, is_staff, or account_type == 'admin').
    Used for all /api/v1/admin/* endpoints.
    """
    message = "Access restricted to Super Admin accounts."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return (
            getattr(request.user, "is_superuser", False)
            or getattr(request.user, "is_staff", False)
            or getattr(request.user, "account_type", "") == "admin"
        )


class IsWorkspaceOwner(BasePermission):
    """
    Object-level permission — ensures the authenticated user owns the workspace.
    Applied to workspace-specific detail/update endpoints.
    """
    message = "You do not have permission to access this workspace."

    def has_object_permission(self, request, view, obj):
        # obj is a GuestWorkspace instance
        return obj.owner == request.user


class IsMobileVerified(BasePermission):
    """
    Requires the authenticated user to have verified their mobile number.
    """
    message = "Mobile number verification is required to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_mobile_verified
        )
