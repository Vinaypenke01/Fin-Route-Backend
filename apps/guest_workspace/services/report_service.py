"""
guest_workspace/services/report_service.py

ReportService handles reporting data aggregation and exports (CSV / PDF) for Guest Workspaces.
"""

import csv
import io
import logging
from django.db.models import Sum, Count

from apps.common.exceptions import BusinessRuleException
from apps.guest_workspace.models import GuestWorkspace, CustomerProfile, CollectionEntry, Expense

logger = logging.getLogger(__name__)


class ReportService:
    """
    Generates reports and export files (CSV/PDF) for Guest Workspace (`app.reports.tsx`).
    """

    @staticmethod
    def generate_collection_report(workspace: GuestWorkspace, params: dict) -> dict:
        """
        Aggregate collection data for a specified date range.
        """
        queryset = CollectionEntry.objects.filter(workspace=workspace).select_related(
            "customer", "status", "payment_mode"
        )

        if date_from := params.get("date_from"):
            queryset = queryset.filter(collection_date__gte=date_from)
        if date_to := params.get("date_to"):
            queryset = queryset.filter(collection_date__lte=date_to)
        if customer_id := params.get("customer"):
            queryset = queryset.filter(customer__public_id=customer_id)

        summary = queryset.aggregate(
            total_collected=Sum("collected_amount"),
            total_expected=Sum("expected_amount"),
            entry_count=Count("id"),
        )

        return {
            "summary": {
                "total_collected": float(summary["total_collected"] or 0),
                "total_expected": float(summary["total_expected"] or 0),
                "total_entries": summary["entry_count"] or 0,
            },
            "entries": queryset[:100],  # Return up to 100 for preview
        }

    @staticmethod
    def generate_customer_report(workspace: GuestWorkspace, params: dict) -> dict:
        """
        Aggregate customer portfolio data.
        """
        queryset = CustomerProfile.objects.filter(workspace=workspace).select_related(
            "collection_frequency", "interest_type"
        )

        if status := params.get("status"):
            queryset = queryset.filter(status=status)

        summary = queryset.aggregate(
            total_customers=Count("id"),
            total_disbursed=Sum("disbursed_amount"),
            total_due=Sum("total_due"),
            total_outstanding=Sum("outstanding_balance"),
        )

        return {
            "summary": {
                "total_customers": summary["total_customers"] or 0,
                "total_disbursed": float(summary["total_disbursed"] or 0),
                "total_due": float(summary["total_due"] or 0),
                "total_outstanding": float(summary["total_outstanding"] or 0),
            },
            "customers": queryset[:100],
        }

    @staticmethod
    def generate_expense_report(workspace: GuestWorkspace, params: dict) -> dict:
        """
        Aggregate expense data by category for a date range.
        """
        queryset = Expense.objects.filter(workspace=workspace).select_related("category")

        if date_from := params.get("date_from"):
            queryset = queryset.filter(expense_date__gte=date_from)
        if date_to := params.get("date_to"):
            queryset = queryset.filter(expense_date__lte=date_to)

        summary = queryset.aggregate(
            total_expense=Sum("amount"),
            total_entries=Count("id"),
        )

        return {
            "summary": {
                "total_expense": float(summary["total_expense"] or 0),
                "total_entries": summary["total_entries"] or 0,
            },
            "expenses": queryset[:100],
        }

    @staticmethod
    def export_report_csv(workspace: GuestWorkspace, report_type: str, params: dict) -> str:
        """
        Generates a CSV string for download.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == "collection":
            report_data = ReportService.generate_collection_report(workspace, params)
            writer.writerow(["Receipt No", "Date", "Customer Code", "Customer Name", "Expected", "Collected", "Status", "Mode"])
            for item in report_data["entries"]:
                writer.writerow([
                    item.receipt_number,
                    item.collection_date.isoformat(),
                    item.customer.customer_code,
                    item.customer.full_name,
                    item.expected_amount,
                    item.collected_amount,
                    item.status.name if item.status else "",
                    item.payment_mode.name if item.payment_mode else "",
                ])

        elif report_type == "customer":
            report_data = ReportService.generate_customer_report(workspace, params)
            writer.writerow(["Customer Code", "Full Name", "Mobile", "Loan Amount", "Total Due", "Outstanding", "Status"])
            for c in report_data["customers"]:
                writer.writerow([
                    c.customer_code,
                    c.full_name,
                    c.mobile_number,
                    c.loan_amount,
                    c.total_due,
                    c.outstanding_balance,
                    c.status,
                ])

        elif report_type == "expense":
            report_data = ReportService.generate_expense_report(workspace, params)
            writer.writerow(["Date", "Category", "Amount", "Description"])
            for e in report_data["expenses"]:
                writer.writerow([
                    e.expense_date.isoformat(),
                    e.category.name if e.category else "",
                    e.amount,
                    e.description,
                ])
        else:
            raise BusinessRuleException("Invalid report type for export.")

        return output.getvalue()
