"""
guest_workspace/services/dashboard_service.py

DashboardService calculates on-demand dashboard metrics for Guest Workspaces:
- Summary cards (total customers, active loans, collections today, outstanding balance, etc.)
- Weekly summary
- Recent collections
"""

import logging
from datetime import date, timedelta
from django.db.models import Sum, Count, Q

from apps.common.utils import get_week_date_range
from apps.guest_workspace.models import (
    GuestWorkspace,
    CustomerProfile,
    CollectionEntry,
    Expense,
    CapitalEntry,
    CustomerStatus,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Computes dashboard analytics for Guest Workspace home screen (`app.index.tsx`).
    """

    @staticmethod
    def get_dashboard_stats(workspace: GuestWorkspace) -> dict:
        """
        Calculates and returns top summary metrics for the workspace dashboard.
        """
        today = date.today()
        week_start, week_end = get_week_date_range(today)
        month_start = today.replace(day=1)

        # Customers & Outstanding
        customer_agg = CustomerProfile.objects.filter(workspace=workspace).aggregate(
            total_customers=Count("id"),
            active_loans=Count("id", filter=Q(status=CustomerStatus.ACTIVE)),
            total_outstanding=Sum("outstanding_balance"),
        )

        # Loan Disbursements Today & This Week
        disbursements_agg = CustomerProfile.objects.filter(
            workspace=workspace,
            start_date=today,
        ).aggregate(
            total_disbursed=Sum("disbursed_amount"),
            count=Count("id"),
        )

        # Capital Injections / Opening Cash Today
        capital_agg = CapitalEntry.objects.filter(
            workspace=workspace,
            entry_date=today,
        ).aggregate(
            total_capital=Sum("amount"),
        )

        # Collections Today
        today_collections = CollectionEntry.objects.filter(
            workspace=workspace,
            collection_date=today,
        ).aggregate(
            count=Count("id"),
            total_collected=Sum("collected_amount"),
            pending_count=Count("id", filter=Q(status__code="pending")),
        )

        # Weekly Collections
        weekly_collections = CollectionEntry.objects.filter(
            workspace=workspace,
            collection_date__gte=week_start,
            collection_date__lte=week_end,
        ).aggregate(
            total_collected=Sum("collected_amount")
        )

        # Today's Expenses
        today_expenses = Expense.objects.filter(
            workspace=workspace,
            expense_date=today,
        ).aggregate(
            total_expense=Sum("amount")
        )

        # Monthly Expenses
        monthly_expenses = Expense.objects.filter(
            workspace=workspace,
            expense_date__gte=month_start,
        ).aggregate(
            total_expense=Sum("amount")
        )

        amount_collected_today = float(today_collections["total_collected"] or 0)
        disbursements_today = float(disbursements_agg["total_disbursed"] or 0)
        expenses_today = float(today_expenses["total_expense"] or 0)
        capital_today = float(capital_agg["total_capital"] or 0)

        # Net Route Cash Position: (Collected + Capital) - (Disbursements + Expenses)
        net_cash_today = (amount_collected_today + capital_today) - (disbursements_today + expenses_today)

        return {
            "total_customers": customer_agg["total_customers"] or 0,
            "active_loans": customer_agg["active_loans"] or 0,
            "collections_today": today_collections["count"] or 0,
            "amount_collected_today": amount_collected_today,
            "amount_collected_this_week": float(weekly_collections["total_collected"] or 0),
            "disbursements_today": disbursements_today,
            "new_borrowers_today": disbursements_agg["count"] or 0,
            "capital_today": capital_today,
            "expenses_today": expenses_today,
            "net_cash_today": net_cash_today,
            "is_cash_deficit": net_cash_today < 0,
            "outstanding_balance": float(customer_agg["total_outstanding"] or 0),
            "pending_today": today_collections["pending_count"] or 0,
            "expenses_this_month": float(monthly_expenses["total_expense"] or 0),
        }

    @staticmethod
    def get_weekly_summary(workspace: GuestWorkspace) -> list:
        """
        Returns collection trends by day for the current week (Monday to Sunday).
        """
        today = date.today()
        week_start, _ = get_week_date_range(today)

        daily_data = []
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_stats = CollectionEntry.objects.filter(
                workspace=workspace,
                collection_date=day_date,
            ).aggregate(
                collected=Sum("collected_amount"),
                count=Count("id"),
            )
            daily_data.append({
                "date": day_date.isoformat(),
                "day_name": day_date.strftime("%a"),
                "amount_collected": float(day_stats["collected"] or 0),
                "count": day_stats["count"] or 0,
            })

        return daily_data

    @staticmethod
    def get_recent_collections(workspace: GuestWorkspace, limit: int = 10):
        """Returns the most recent collection entries."""
        return CollectionEntry.objects.filter(
            workspace=workspace
        ).select_related(
            "customer", "status", "payment_mode"
        ).order_by("-collection_date", "-created_at")[:limit]
