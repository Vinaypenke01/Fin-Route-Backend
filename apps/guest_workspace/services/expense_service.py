"""
guest_workspace/services/expense_service.py

ExpenseService handles workspace operational expenses:
- Creating, listing, updating, deleting expenses
- Managing custom workspace-scoped expense categories
"""

import logging
from django.db import transaction

from apps.common.exceptions import ExpenseNotFoundException, BusinessRuleException
from apps.guest_workspace.models import Expense, GuestWorkspace

logger = logging.getLogger(__name__)


class ExpenseService:
    """
    Manages operational expenses for a Guest Workspace.
    """

    @staticmethod
    @transaction.atomic
    def create_expense(
        workspace: GuestWorkspace,
        validated_data: dict,
        created_by,
    ) -> Expense:
        """Create a new expense entry for the workspace."""
        data = dict(validated_data)

        raw_category = data.pop("category", None)
        category_id = int(raw_category) if raw_category is not None else None

        raw_mode = data.pop("payment_mode", None)
        mode_id = int(raw_mode) if raw_mode is not None else None

        expense = Expense.objects.create(
            workspace=workspace,
            created_by=created_by,
            category_id=category_id,
            payment_mode_id=mode_id,
            **data,
        )
        logger.info(
            "Expense recorded: amount=%s category=%s workspace=%s",
            expense.amount,
            expense.category_id,
            workspace.name,
        )
        return expense

    @staticmethod
    def get_expenses(workspace: GuestWorkspace, filters: dict = None):
        """
        Return paginated expenses for a workspace with optional filters.

        Supported filters:
        - date_from / date_to
        - category (ID or code)
        - payment_mode
        """
        queryset = Expense.objects.filter(
            workspace=workspace
        ).select_related("category", "payment_mode", "created_by")

        if filters:
            if date_from := filters.get("date_from"):
                queryset = queryset.filter(expense_date__gte=date_from)
            if date_to := filters.get("date_to"):
                queryset = queryset.filter(expense_date__lte=date_to)
            if category := filters.get("category"):
                if str(category).isdigit():
                    queryset = queryset.filter(category_id=int(category))
                else:
                    queryset = queryset.filter(category__code=category)
            if payment_mode := filters.get("payment_mode"):
                if str(payment_mode).isdigit():
                    queryset = queryset.filter(payment_mode_id=int(payment_mode))
                else:
                    queryset = queryset.filter(payment_mode__code=payment_mode)

        return queryset

    @staticmethod
    def get_expense_detail(workspace: GuestWorkspace, expense_public_id: str) -> Expense:
        """Fetch a single expense record by public_id."""
        try:
            return Expense.objects.select_related(
                "category", "payment_mode", "created_by"
            ).get(workspace=workspace, public_id=expense_public_id)
        except Expense.DoesNotExist:
            raise ExpenseNotFoundException()

    @staticmethod
    @transaction.atomic
    def update_expense(
        workspace: GuestWorkspace,
        expense_public_id: str,
        validated_data: dict,
    ) -> Expense:
        """Update an existing expense record."""
        expense = ExpenseService.get_expense_detail(workspace, expense_public_id)
        data = dict(validated_data)

        if "category" in data:
            raw_category = data.pop("category")
            expense.category_id = int(raw_category) if raw_category is not None else None

        if "payment_mode" in data:
            raw_mode = data.pop("payment_mode")
            expense.payment_mode_id = int(raw_mode) if raw_mode is not None else None

        for field, value in data.items():
            setattr(expense, field, value)
        expense.save()

        return expense

    @staticmethod
    @transaction.atomic
    def delete_expense(workspace: GuestWorkspace, expense_public_id: str) -> None:
        """Delete an expense record."""
        expense = ExpenseService.get_expense_detail(workspace, expense_public_id)
        expense.delete()
        logger.info("Expense deleted: %s", expense_public_id)
