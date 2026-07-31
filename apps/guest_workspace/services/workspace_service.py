"""
guest_workspace/services/workspace_service.py

GuestWorkspaceService handles all workspace-level business logic:
- Creating default workspaces on registration
- Retrieving workspace settings
- Enforcing plan limits (quota checks)
"""

import logging
from django.db import transaction

from apps.common.exceptions import (
    PlanLimitExceededException,
    WorkspaceNotFoundException,
    WorkspaceSuspendedException,
    BusinessRuleException,
)
from apps.guest_workspace.models import GuestWorkspace, WorkspaceStatus, SubscriptionPlan

logger = logging.getLogger(__name__)

# ─── Plan Default Limits ──────────────────────────────────────────────────────
# These are the platform defaults. Super Admin can override per workspace.

FREE_PLAN_DEFAULTS = {
    "max_customers": 50,
    "max_collection_days_per_week": 2,
    "can_export_reports": False,
    "can_batch_collect": True,
}

PREMIUM_PLAN_DEFAULTS = {
    "max_customers": None,      # Unlimited
    "max_collection_days_per_week": None,  # Unlimited
    "can_export_reports": True,
    "can_batch_collect": True,
}


class GuestWorkspaceService:
    """
    Manages the lifecycle and limits of Guest Workspaces.
    """

    @staticmethod
    @transaction.atomic
    def create_default_workspace(owner, name: str = None) -> GuestWorkspace:
        """
        Create the default GuestWorkspace for a newly registered user.
        Called atomically inside AccountService.register_guest().

        Args:
            owner: The User instance who owns this workspace.
            name: Optional workspace name. Defaults to "{owner.full_name} Finance".

        Returns:
            Newly created GuestWorkspace instance.
        """
        if GuestWorkspace.objects.filter(owner=owner).exists():
            raise BusinessRuleException("A workspace already exists for this account.")

        workspace_name = name or f"{owner.full_name} Finance"

        workspace = GuestWorkspace.objects.create(
            owner=owner,
            name=workspace_name,
            mobile_number=owner.mobile_number,
            subscription_plan=SubscriptionPlan.FREE,
            status=WorkspaceStatus.ACTIVE,
        )

        logger.info("Default workspace created for user=%s", owner.mobile_number)
        return workspace

    @staticmethod
    def get_workspace(user) -> GuestWorkspace:
        """
        Retrieve the authenticated user's workspace.

        Raises:
            WorkspaceNotFoundException if not found.
            WorkspaceSuspendedException if suspended.
        """
        try:
            workspace = GuestWorkspace.objects.select_related(
                "owner", "business_category"
            ).get(owner=user)
        except GuestWorkspace.DoesNotExist:
            raise WorkspaceNotFoundException()

        if workspace.status == WorkspaceStatus.SUSPENDED:
            raise WorkspaceSuspendedException()

        return workspace

    @staticmethod
    def get_effective_limits(workspace: GuestWorkspace) -> dict:
        """
        Calculate the effective plan limits for a workspace.
        Admin overrides take precedence over plan defaults.

        Returns:
            dict with max_customers, max_collection_days_per_week, base_free_days, purchased_additional_days.
        """
        max_days = workspace.max_allowed_collection_days
        base = {
            "max_customers": workspace.max_customers_override,  # None = Unlimited for all guest users
            "max_collection_days_per_week": max_days,
            "base_free_days": 1,
            "purchased_additional_days": workspace.purchased_additional_days,
            "total_allowed_days": max_days,
        }
        return base

    @staticmethod
    def check_customer_quota(workspace: GuestWorkspace) -> None:
        """
        Check if the workspace can add another customer.

        Raises:
            PlanLimitExceededException if the customer limit is reached.
        """
        limits = GuestWorkspaceService.get_effective_limits(workspace)
        max_customers = limits["max_customers"]

        if max_customers is None:
            return  # Unlimited

        current_count = workspace.customers.filter(
            status__in=["active", "defaulted"]
        ).count()

        if current_count >= max_customers:
            raise PlanLimitExceededException(
                detail=f"Customer limit of {max_customers} reached on your current plan.",
                usage={"current_customers": current_count, "limit": max_customers},
            )

    @staticmethod
    def check_collection_day_quota(workspace: GuestWorkspace, collection_date) -> None:
        """
        Check if a new collection can be recorded on the given date
        without exceeding the weekly collection day limit.

        The "week" is ISO week (Monday to Sunday).

        Raises:
            PlanLimitExceededException if weekly day limit is reached.
        """
        from apps.common.utils import get_week_date_range
        from apps.guest_workspace.models import CollectionEntry
        import datetime

        limits = GuestWorkspaceService.get_effective_limits(workspace)
        max_days = limits["max_collection_days_per_week"] or 1

        if max_days >= 7:
            return  # Unlimited 7 days

        # Check if the weekday of collection_date is in workspace.allowed_collection_days
        allowed_days = [d.lower() for d in (workspace.allowed_collection_days or [])]
        if allowed_days:
            c_date_obj = collection_date
            if isinstance(c_date_obj, str):
                try:
                    c_date_obj = datetime.datetime.strptime(c_date_obj, "%Y-%m-%d").date()
                except ValueError:
                    pass
            weekday_name = c_date_obj.strftime("%A").lower() if hasattr(c_date_obj, "strftime") else ""
            if weekday_name in allowed_days:
                return  # Configured operating day for this workspace!

        week_start, week_end = get_week_date_range(collection_date)

        # Count distinct collection days in the current ISO week
        distinct_days = (
            CollectionEntry.objects.filter(
                workspace=workspace,
                collection_date__gte=week_start,
                collection_date__lte=week_end,
            )
            .values("collection_date")
            .distinct()
            .count()
        )

        # If today's date is already one of the existing days, allow it
        existing_today = CollectionEntry.objects.filter(
            workspace=workspace,
            collection_date=collection_date,
        ).exists()

        if not existing_today and distinct_days >= max_days:
            raise PlanLimitExceededException(
                detail=f"You have reached your limit of {max_days} collection business day(s) per week. Upgrade your plan to purchase additional collection days.",
                usage={
                    "collection_days_this_week": distinct_days,
                    "limit": max_days,
                },
            )

    @staticmethod
    @transaction.atomic
    def update_workspace(workspace: GuestWorkspace, validated_data: dict) -> GuestWorkspace:
        """Update workspace settings and auto-remap customer collection routes when operating days change."""
        allowed_fields = ["name", "business_category", "mobile_number", "logo",
                         "address", "city", "state", "pin_code", "allowed_collection_days"]
        
        old_days = workspace.allowed_collection_days or []
        new_days = validated_data.get("allowed_collection_days")

        for field in allowed_fields:
            if field in validated_data:
                setattr(workspace, field, validated_data[field])
        workspace.save()

        # Auto-remap active borrowers if operating collection days were updated
        if new_days is not None and isinstance(new_days, list) and len(new_days) > 0:
            from apps.guest_workspace.models import CustomerProfile
            primary_new_day = new_days[0].lower()
            updated_count = CustomerProfile.objects.filter(workspace=workspace).exclude(
                collection_day__in=[d.lower() for d in new_days]
            ).update(collection_day=primary_new_day)
            
            if updated_count > 0:
                logger.info(
                    "Auto-remapped %d borrower(s) in workspace=%s to new primary day=%s",
                    updated_count, workspace.name, primary_new_day
                )

        return workspace
