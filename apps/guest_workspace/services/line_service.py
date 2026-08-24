"""
guest_workspace/services/line_service.py

LineService manages Collection Lines (Business Routes) and Day Portions:
- Creating/updating Lines with assigned weekday portions (Morning 1am-1pm / Afternoon 1pm-12am / Both)
- Capacity & conflict validation: Ensures day portions are not double-booked across lines
- Zero-disruption production migration: Automatically builds a Default Line for legacy production workspaces
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import QuerySet

from apps.common.exceptions import BusinessRuleException
from apps.guest_workspace.models import (
    GuestWorkspace,
    CollectionLine,
    LineDaySchedule,
    DayPortionChoices,
    CustomerProfile,
)

logger = logging.getLogger(__name__)


class LineService:
    """
    Business logic service for managing Collection Lines and Day Portions.
    """

    @staticmethod
    def get_lines(workspace: GuestWorkspace) -> QuerySet:
        """
        Fetch active collection lines with pre-fetched day schedules for a workspace.
        """
        return (
            CollectionLine.objects.filter(workspace=workspace, is_active=True)  # type: ignore
            .prefetch_related("day_schedules")
            .order_by("created_at")
        )

    @staticmethod
    def get_line_detail(workspace: GuestWorkspace, line_public_id: str) -> CollectionLine:
        """
        Fetch a single collection line by public_id.
        """
        try:
            return CollectionLine.objects.prefetch_related("day_schedules").get(  # type: ignore
                workspace=workspace, public_id=line_public_id, is_active=True
            )
        except CollectionLine.DoesNotExist:  # type: ignore
            raise BusinessRuleException("Collection line not found.")

    @staticmethod
    def validate_portion_availability(
        workspace: GuestWorkspace,
        day_of_week: str,
        requested_portion: str,
        exclude_line_id: Optional[int] = None,
    ) -> bool:
        """
        Validates that (day_of_week, requested_portion) is available and not taken by another Line.
        Rules:
        - If existing line uses 'both', no other line can book that day.
        - If existing line uses 'morning', another line can only book 'afternoon'.
        - If existing line uses 'afternoon', another line can only book 'morning'.
        """
        schedules = LineDaySchedule.objects.filter(  # type: ignore
            line__workspace=workspace,
            line__is_active=True,
            day_of_week=day_of_week.lower(),
        )
        if exclude_line_id:
            schedules = schedules.exclude(line_id=exclude_line_id)

        for sched in schedules:
            existing = sched.portion
            if existing == DayPortionChoices.BOTH or requested_portion == DayPortionChoices.BOTH:
                return False
            if existing == requested_portion:
                return False

        return True

    @staticmethod
    def get_available_day_portions(workspace: GuestWorkspace, exclude_line_id: Optional[int] = None) -> Dict[str, List[str]]:
        """
        Returns available portions for each weekday (monday..sunday) in the workspace.
        """
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        result = {}
        for day in days:
            available = []
            if LineService.validate_portion_availability(workspace, day, DayPortionChoices.MORNING, exclude_line_id):
                available.append("morning")
            if LineService.validate_portion_availability(workspace, day, DayPortionChoices.AFTERNOON, exclude_line_id):
                available.append("afternoon")
            if LineService.validate_portion_availability(workspace, day, DayPortionChoices.BOTH, exclude_line_id):
                available.append("both")
            result[day] = available
        return result

    @staticmethod
    def validate_workspace_plan_limits(
        workspace: GuestWorkspace,
        new_or_updated_schedules: Optional[List[Dict[str, str]]],
        exclude_line_id: Optional[int] = None,
    ) -> None:
        """
        Validates line creation and weekday schedules against workspace subscription plan limits.
        Rules:
        - Free Plan: Up to max_allowed_collection_days (default 2 days / 4 sessions max).
        - Premium / Upgraded Plan: Unlimited collection days (all 7 days) and unlimited route lines.
        """
        sub_plan = (getattr(workspace, "subscription_plan", "free") or "free").lower()
        if sub_plan in ["free", "guest"]:
            max_allowed_days = getattr(workspace, "max_allowed_collection_days", 2) or 2
            
            # Fetch existing active day schedules across all other lines
            existing_schedules_qs = LineDaySchedule.objects.filter(  # type: ignore
                line__workspace=workspace,
                line__is_active=True,
            )
            if exclude_line_id:
                existing_schedules_qs = existing_schedules_qs.exclude(line_id=exclude_line_id)

            existing_days = set(existing_schedules_qs.values_list("day_of_week", flat=True))
            new_days = {s.get("day_of_week", "").lower() for s in (new_or_updated_schedules or []) if s.get("day_of_week")}
            
            combined_days = existing_days.union(new_days)

            if len(combined_days) > max_allowed_days:
                raise BusinessRuleException(
                    f"Your FREE plan permits operating on a maximum of {max_allowed_days} collection days per week "
                    f"({len(combined_days)} requested). Please upgrade your plan to unlock all 7 collection days and unlimited route lines!"
                )

    @staticmethod
    @transaction.atomic
    def create_line(
        workspace: GuestWorkspace,
        name: str,
        area: str = "",
        schedules: Optional[List[Dict[str, str]]] = None,
        created_by=None,
    ) -> CollectionLine:
        """
        Create a new Collection Line with weekday portion schedules.
        """
        if not name or not name.strip():
            raise BusinessRuleException("Line name is required.")

        schedules = schedules or []

        # Validate workspace subscription plan limits (sessions & days)
        LineService.validate_workspace_plan_limits(workspace, schedules)

        # Validate capacity for each requested schedule against existing lines
        for sched in schedules:
            day = (sched.get("day_of_week") or "").lower()
            portion = (sched.get("portion") or DayPortionChoices.BOTH).lower()
            if not LineService.validate_portion_availability(workspace, day, portion):
                raise BusinessRuleException(
                    f"The {portion.upper()} portion of {day.capitalize()} is already booked by another line."
                )

        line = CollectionLine.objects.create(  # type: ignore
            workspace=workspace,
            name=name.strip(),
            area=area.strip(),
            created_by=created_by or workspace.owner,
        )

        for sched in schedules:
            day = (sched.get("day_of_week") or "").lower()
            portion = (sched.get("portion") or DayPortionChoices.BOTH).lower()
            LineDaySchedule.objects.create(  # type: ignore
                line=line,
                day_of_week=day,
                portion=portion,
            )

        logger.info("Created CollectionLine '%s' (ID: %s) for workspace '%s'", line.name, line.public_id, workspace.name)
        LineService.sync_workspace_allowed_days(workspace)
        return line

    @staticmethod
    def sync_workspace_allowed_days(workspace: GuestWorkspace) -> None:
        """
        Auto-syncs workspace.allowed_collection_days based on active collection lines.
        """
        days = list(
            LineDaySchedule.objects.filter(line__workspace=workspace, line__is_active=True)  # type: ignore
            .values_list("day_of_week", flat=True)
            .distinct()
        )
        if days:
            workspace.allowed_collection_days = days
            workspace.save(update_fields=["allowed_collection_days"])

    @staticmethod
    @transaction.atomic
    def update_line(
        workspace: GuestWorkspace,
        line_public_id: str,
        name: Optional[str] = None,
        area: Optional[str] = None,
        schedules: Optional[List[Dict[str, str]]] = None,
    ) -> CollectionLine:
        """
        Update an existing Collection Line.
        """
        line = LineService.get_line_detail(workspace, line_public_id)

        if name is not None:
            line.name = name.strip()
        if area is not None:
            line.area = area.strip()
        line.save()

        if schedules is not None:
            # Validate workspace subscription plan limits excluding current line
            LineService.validate_workspace_plan_limits(workspace, schedules, exclude_line_id=line.id)

            # Validate capacity excluding current line
            for sched in schedules:
                day = (sched.get("day_of_week") or "").lower()
                portion = (sched.get("portion") or DayPortionChoices.BOTH).lower()
                if not LineService.validate_portion_availability(workspace, day, portion, exclude_line_id=line.id):
                    raise BusinessRuleException(
                        f"The {portion.upper()} portion of {day.capitalize()} is already booked by another line."
                    )

            # Re-create schedules
            line.day_schedules.all().delete()  # type: ignore
            for sched in schedules:
                day = (sched.get("day_of_week") or "").lower()
                portion = (sched.get("portion") or DayPortionChoices.BOTH).lower()
                LineDaySchedule.objects.create(  # type: ignore
                    line=line,
                    day_of_week=day,
                    portion=portion,
                )

        LineService.sync_workspace_allowed_days(workspace)
        return line

    @staticmethod
    @transaction.atomic
    def delete_line(
        workspace: GuestWorkspace,
        line_public_id: str,
        mode: str = "unassign",
        target_line_public_id: Optional[str] = None,
    ) -> None:
        """
        Deactivate / delete a line.
        - mode='reassign': Move linked customers to target_line_public_id
        - mode='delete_customers': Permanently delete all linked customers & payment records
        - mode='unassign': Set customer.line = None
        """
        from apps.guest_workspace.models import CustomerProfile
        line = LineService.get_line_detail(workspace, line_public_id)

        if mode == "reassign" and target_line_public_id:
            try:
                target_line = CollectionLine.objects.get(workspace=workspace, public_id=target_line_public_id, is_active=True)  # type: ignore
                CustomerProfile.objects.filter(workspace=workspace, line=line).update(line=target_line)  # type: ignore
            except CollectionLine.DoesNotExist:  # type: ignore
                raise BusinessRuleException("Target route line for reassignment not found.")
        elif mode == "delete_customers":
            # Hard delete customers linked to this line as well as any unassigned customers & their CASCADE collection entries
            CustomerProfile.objects.filter(workspace=workspace, line=line).delete()  # type: ignore
            CustomerProfile.objects.filter(workspace=workspace, line__isnull=True).delete()  # type: ignore

        line.is_active = False
        line.save()
        logger.info("Deactivated CollectionLine '%s' (ID: %s, mode: %s)", line.name, line.public_id, mode)
        LineService.sync_workspace_allowed_days(workspace)

    @staticmethod
    @transaction.atomic
    def ensure_default_line_for_workspace(workspace: GuestWorkspace) -> CollectionLine:
        """
        Zero-Disruption Migration:
        Ensures existing production workspaces have at least one Line ("Main Line").
        Maps existing workspace.allowed_collection_days and existing CustomerProfile entries to this Line.
        """
        existing_line = CollectionLine.objects.filter(workspace=workspace, is_active=True).first()  # type: ignore
        if existing_line:
            return existing_line

        line_name = f"{workspace.name} — Main Line" if workspace.name else "Main Line"
        default_line = CollectionLine.objects.create(  # type: ignore
            workspace=workspace,
            name=line_name,
            area=workspace.city or "Main Route",
            created_by=workspace.owner,
        )

        saved_days = workspace.allowed_collection_days or ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in saved_days:
            LineDaySchedule.objects.create(  # type: ignore
                line=default_line,
                day_of_week=str(day).lower(),
                portion=DayPortionChoices.BOTH,
            )

        # Map unassigned existing customer profiles to this Default Line
        CustomerProfile.objects.filter(workspace=workspace, line__isnull=True).update(  # type: ignore
            line=default_line,
            portion=DayPortionChoices.BOTH,
        )

        logger.info("Zero-Disruption Auto-Migration: Created default line '%s' for workspace '%s'", default_line.name, workspace.name)
        return default_line
