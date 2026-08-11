"""
guest_workspace/services/line_service.py

LineService manages Collection Lines (Business Routes) and Day Portions:
- Creating/updating Lines with assigned weekday portions (Morning 1am-1pm / Afternoon 1pm-12am / Both)
- Capacity & conflict validation: Ensures day portions are not double-booked across lines
- Zero-disruption production migration: Automatically builds a Default Line for legacy production workspaces
"""

import logging
from typing import List, Dict, Any
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
            CollectionLine.objects.filter(workspace=workspace, is_active=True)
            .prefetch_related("day_schedules")
            .order_by("created_at")
        )

    @staticmethod
    def get_line_detail(workspace: GuestWorkspace, line_public_id: str) -> CollectionLine:
        """
        Fetch a single collection line by public_id.
        """
        try:
            return CollectionLine.objects.prefetch_related("day_schedules").get(
                workspace=workspace, public_id=line_public_id, is_active=True
            )
        except CollectionLine.DoesNotExist:
            raise BusinessRuleException("Collection line not found.")

    @staticmethod
    def validate_portion_availability(
        workspace: GuestWorkspace,
        day_of_week: str,
        requested_portion: str,
        exclude_line_id: int = None,
    ) -> bool:
        """
        Validates that (day_of_week, requested_portion) is available and not taken by another Line.
        Rules:
        - If existing line uses 'both', no other line can book that day.
        - If existing line uses 'morning', another line can only book 'afternoon'.
        - If existing line uses 'afternoon', another line can only book 'morning'.
        """
        schedules = LineDaySchedule.objects.filter(
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
    def get_available_day_portions(workspace: GuestWorkspace, exclude_line_id: int = None) -> Dict[str, List[str]]:
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
        new_or_updated_schedules: List[Dict[str, str]],
        exclude_line_id: int = None,
    ) -> None:
        """
        Validates that total active collection sessions and unique days across ALL active lines
        in the workspace do NOT exceed workspace.max_allowed_collection_days (Plan limit).
        Rules:
        - max_allowed_days = workspace.max_allowed_collection_days
        - max_allowed_sessions = max_allowed_days * 2
        - portion 'both' counts as 2 sessions (1.0 full day).
        - portion 'morning' or 'afternoon' counts as 1 session (0.5 day).
        """
        existing_schedules_qs = LineDaySchedule.objects.filter(
            line__workspace=workspace,
            line__is_active=True,
        )
        if exclude_line_id:
            existing_schedules_qs = existing_schedules_qs.exclude(line_id=exclude_line_id)

        existing_schedules = list(existing_schedules_qs.values("day_of_week", "portion"))

        combined_schedules = existing_schedules + [
            {
                "day_of_week": s.get("day_of_week", "").lower(),
                "portion": s.get("portion", DayPortionChoices.BOTH).lower(),
            }
            for s in new_or_updated_schedules
        ]

        total_sessions = 0
        unique_days = set()

        for s in combined_schedules:
            day = s.get("day_of_week")
            portion = s.get("portion")
            if not day:
                continue
            unique_days.add(day)
            if portion == DayPortionChoices.BOTH:
                total_sessions += 2
            else:
                total_sessions += 1

        max_allowed_days = workspace.max_allowed_collection_days
        max_allowed_sessions = max_allowed_days * 2

        if total_sessions > max_allowed_sessions:
            raise BusinessRuleException(
                f"Your {workspace.subscription_plan.capitalize()} plan allows up to {max_allowed_sessions} session(s) max per week "
                f"({max_allowed_days} full day equivalent). Your configured route schedules require {total_sessions} session(s). "
                f"Please upgrade your plan to unlock more collection sessions or routes."
            )

    @staticmethod
    @transaction.atomic
    def create_line(
        workspace: GuestWorkspace,
        name: str,
        area: str = "",
        schedules: List[Dict[str, str]] = None,
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
            day = sched.get("day_of_week", "").lower()
            portion = sched.get("portion", DayPortionChoices.BOTH).lower()
            if not LineService.validate_portion_availability(workspace, day, portion):
                raise BusinessRuleException(
                    f"The {portion.upper()} portion of {day.capitalize()} is already booked by another line."
                )

        line = CollectionLine.objects.create(
            workspace=workspace,
            name=name.strip(),
            area=area.strip(),
            created_by=created_by or workspace.owner,
        )

        for sched in schedules:
            day = sched.get("day_of_week", "").lower()
            portion = sched.get("portion", DayPortionChoices.BOTH).lower()
            LineDaySchedule.objects.create(
                line=line,
                day_of_week=day,
                portion=portion,
            )

        logger.info("Created CollectionLine '%s' (ID: %s) for workspace '%s'", line.name, line.public_id, workspace.name)
        return line

    @staticmethod
    @transaction.atomic
    def update_line(
        workspace: GuestWorkspace,
        line_public_id: str,
        name: str = None,
        area: str = None,
        schedules: List[Dict[str, str]] = None,
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
                day = sched.get("day_of_week", "").lower()
                portion = sched.get("portion", DayPortionChoices.BOTH).lower()
                if not LineService.validate_portion_availability(workspace, day, portion, exclude_line_id=line.id):
                    raise BusinessRuleException(
                        f"The {portion.upper()} portion of {day.capitalize()} is already booked by another line."
                    )

            # Re-create schedules
            line.day_schedules.all().delete()
            for sched in schedules:
                day = sched.get("day_of_week", "").lower()
                portion = sched.get("portion", DayPortionChoices.BOTH).lower()
                LineDaySchedule.objects.create(
                    line=line,
                    day_of_week=day,
                    portion=portion,
                )

        return line

    @staticmethod
    @transaction.atomic
    def delete_line(workspace: GuestWorkspace, line_public_id: str) -> None:
        """
        Soft-delete / deactivate a line.
        """
        line = LineService.get_line_detail(workspace, line_public_id)
        line.is_active = False
        line.save()
        logger.info("Deactivated CollectionLine '%s' (ID: %s)", line.name, line.public_id)

    @staticmethod
    @transaction.atomic
    def ensure_default_line_for_workspace(workspace: GuestWorkspace) -> CollectionLine:
        """
        Zero-Disruption Migration:
        Ensures existing production workspaces have at least one Line ("Main Line").
        Maps existing workspace.allowed_collection_days and existing CustomerProfile entries to this Line.
        """
        existing_line = CollectionLine.objects.filter(workspace=workspace, is_active=True).first()
        if existing_line:
            return existing_line

        line_name = f"{workspace.name} — Main Line" if workspace.name else "Main Line"
        default_line = CollectionLine.objects.create(
            workspace=workspace,
            name=line_name,
            area=workspace.city or "Main Route",
            created_by=workspace.owner,
        )

        saved_days = workspace.allowed_collection_days or ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in saved_days:
            LineDaySchedule.objects.create(
                line=default_line,
                day_of_week=day.lower(),
                portion=DayPortionChoices.BOTH,
            )

        # Map unassigned existing customer profiles to this Default Line
        CustomerProfile.objects.filter(workspace=workspace, line__isnull=True).update(
            line=default_line,
            portion=DayPortionChoices.BOTH,
        )

        logger.info("Zero-Disruption Auto-Migration: Created default line '%s' for workspace '%s'", default_line.name, workspace.name)
        return default_line
