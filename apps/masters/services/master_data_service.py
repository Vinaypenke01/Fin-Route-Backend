"""
masters/services/master_data_service.py

MasterDataService handles retrieval and management of platform reference data.
Seeds initial default values if DB is empty.
"""

import logging
from django.db.models import Q
from apps.masters.models import (
    CollectionFrequency,
    InterestType,
    PaymentMode,
    CollectionStatus,
    ExpenseCategory,
    BusinessCategory,
)

logger = logging.getLogger(__name__)


class MasterDataService:
    """
    Manages domain master data lookup lists.
    """

    @staticmethod
    def get_collection_frequencies():
        """Retrieve active collection frequencies."""
        MasterDataService._ensure_seeds()
        return CollectionFrequency.objects.filter(is_active=True).order_by("sort_order")

    @staticmethod
    def get_interest_types():
        """Retrieve active interest types."""
        MasterDataService._ensure_seeds()
        return InterestType.objects.filter(is_active=True)

    @staticmethod
    def get_payment_modes():
        """Retrieve active payment modes."""
        MasterDataService._ensure_seeds()
        return PaymentMode.objects.filter(is_active=True).order_by("sort_order")

    @staticmethod
    def get_collection_statuses():
        """Retrieve collection statuses."""
        MasterDataService._ensure_seeds()
        return CollectionStatus.objects.all().order_by("sort_order")

    @staticmethod
    def get_expense_categories(workspace=None):
        """
        Retrieve expense categories: system default categories + workspace custom categories.
        """
        MasterDataService._ensure_seeds()
        if workspace:
            return ExpenseCategory.objects.filter(
                Q(is_system=True) | Q(workspace=workspace),
                is_active=True,
            ).order_by("name")
        return ExpenseCategory.objects.filter(is_system=True, is_active=True).order_by("name")

    @staticmethod
    def get_business_categories():
        """Retrieve active business categories."""
        MasterDataService._ensure_seeds()
        return BusinessCategory.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def _ensure_seeds():
        """Autoseeds core reference data if tables are empty (convenience for dev)."""
        if not CollectionFrequency.objects.exists():
            CollectionFrequency.objects.bulk_create([
                CollectionFrequency(code="daily", name="Daily", sort_order=1),
                CollectionFrequency(code="weekly", name="Weekly", sort_order=2),
                CollectionFrequency(code="monthly", name="Monthly", sort_order=3),
            ])

        if not InterestType.objects.exists():
            InterestType.objects.bulk_create([
                InterestType(code="flat_percentage", name="Flat Percentage", description="Interest as flat % of loan amount"),
                InterestType(code="fixed_amount", name="Fixed Interest Amount", description="Fixed rupee interest amount"),
                InterestType(code="monthly_percentage", name="Monthly Percentage", description="Interest % charged per month"),
            ])

        if not PaymentMode.objects.exists():
            PaymentMode.objects.bulk_create([
                PaymentMode(code="cash", name="Cash", sort_order=1),
                PaymentMode(code="upi", name="UPI / QR Code", sort_order=2),
                PaymentMode(code="bank_transfer", name="Bank Transfer (NEFT/IMPS)", sort_order=3),
                PaymentMode(code="cheque", name="Cheque", sort_order=4),
                PaymentMode(code="other", name="Other", sort_order=5),
            ])

        if not CollectionStatus.objects.exists():
            CollectionStatus.objects.bulk_create([
                CollectionStatus(code="paid", name="Paid in Full", affects_outstanding=True, sort_order=1),
                CollectionStatus(code="partial", name="Partially Paid", affects_outstanding=True, sort_order=2),
                CollectionStatus(code="pending", name="Pending", affects_outstanding=False, sort_order=3),
                CollectionStatus(code="defaulted", name="Defaulted / Overdue", affects_outstanding=False, requires_reason=True, sort_order=4),
                CollectionStatus(code="skipped", name="Skipped / Promised Later", affects_outstanding=False, sort_order=5),
            ])

        if not ExpenseCategory.objects.exists():
            ExpenseCategory.objects.bulk_create([
                ExpenseCategory(code="fuel", name="Fuel & Petrol", is_system=True),
                ExpenseCategory(code="food", name="Food & Tea", is_system=True),
                ExpenseCategory(code="travel", name="Travel & Conveyance", is_system=True),
                ExpenseCategory(code="office", name="Office Supplies & Print", is_system=True),
                ExpenseCategory(code="salary", name="Employee Salary", is_system=True),
                ExpenseCategory(code="other", name="Other Expenses", is_system=True),
            ])

        if not BusinessCategory.objects.exists():
            BusinessCategory.objects.bulk_create([
                BusinessCategory(code="money_lending", name="Money Lending (Private)"),
                BusinessCategory(code="pawn_broking", name="Pawn Broking / Gold Loan"),
                BusinessCategory(code="microfinance", name="Microfinance"),
                BusinessCategory(code="vehicle_finance", name="Vehicle Finance"),
                BusinessCategory(code="other", name="General Finance"),
            ])
