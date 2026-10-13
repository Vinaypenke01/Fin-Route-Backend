"""
guest_workspace/services/capital_service.py

CapitalService manages starting route cash and capital injections:
- Record capital entries (e.g. +₹10,000 opening cash for a route day)
- List and filter capital entries
- Delete capital entries
"""

import logging
from datetime import date
from typing import Optional
from django.db.models import QuerySet  # type: ignore

from apps.common.exceptions import BusinessRuleException
from apps.guest_workspace.models import GuestWorkspace, CapitalEntry

logger = logging.getLogger(__name__)


class CapitalService:
    """
    Business logic service for managing Capital Entries (Opening Cash / Capital Injections).
    """

    @staticmethod
    def record_capital(
        workspace: GuestWorkspace,
        entry_date: date,
        amount: float,
        remarks: str = "",
        added_by=None,
    ) -> CapitalEntry:
        """
        Record a starting cash / capital entry for the workspace.
        """
        if amount <= 0:
            raise BusinessRuleException("Capital amount must be greater than ₹0.")

        entry = CapitalEntry.objects.create(  # type: ignore
            workspace=workspace,
            entry_date=entry_date,
            amount=amount,
            remarks=remarks,
            added_by=added_by or workspace.owner,
        )
        logger.info(f"Recorded capital entry ₹{amount} for workspace '{workspace.name}' on {entry_date}")
        return entry

    @staticmethod
    def get_capital_entries(
        workspace: GuestWorkspace,
        entry_date: Optional[date] = None,
    ) -> QuerySet:
        """
        Fetch capital entries for the workspace, optionally filtered by date.
        """
        qs = CapitalEntry.objects.filter(workspace=workspace)  # type: ignore
        if entry_date:
            qs = qs.filter(entry_date=entry_date)
        return qs.select_related("added_by")

    @staticmethod
    def delete_capital(workspace: GuestWorkspace, public_id: str) -> bool:
        """
        Delete a capital entry by public_id.
        """
        try:
            entry = CapitalEntry.objects.get(workspace=workspace, public_id=public_id)  # type: ignore
            entry.delete()
            return True
        except CapitalEntry.DoesNotExist:  # type: ignore
            raise BusinessRuleException("Capital entry not found.")
