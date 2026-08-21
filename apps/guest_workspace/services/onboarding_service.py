"""
guest_workspace/services/onboarding_service.py

Service layer for Digital Migration & Existing Borrower Onboarding Suite.

Provides:
- Day 1 Cutover Baseline initialization (physical cash float setup)
- Bulk existing borrower onboarding with pre-digital payment history
- Optional historical net adjustment recording
"""

from datetime import timedelta
from decimal import Decimal
import logging
from django.db import transaction
from django.utils import timezone
from apps.guest_workspace.models import (
    GuestWorkspace,
    CustomerProfile,
    CapitalEntry,
    Expense,
    CollectionLine,
    CustomerStatus,
    CollectionDayChoices,
)
from apps.guest_workspace.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class OnboardingService:
    @transaction.atomic
    def initialize_cutover_baseline(self, workspace: GuestWorkspace, cutover_date, opening_cash: Decimal, user):
        """
        Establishes Day 1 Cutover Baseline.
        Creates a CapitalEntry representing physical handheld cash float on Day 1.
        """
        opening_cash = Decimal(str(opening_cash or 0))

        # Check if an opening migration baseline capital entry already exists on this date
        capital_entry = CapitalEntry.objects.filter(
            workspace=workspace,
            remarks__icontains="Migration Opening Balance",
        ).first()

        if capital_entry:
            capital_entry.amount = opening_cash
            capital_entry.entry_date = cutover_date
            capital_entry.remarks = f"Migration Opening Balance Baseline ({cutover_date})"
            capital_entry.save(update_fields=["amount", "entry_date", "remarks", "updated_at"])
        else:
            capital_entry = CapitalEntry.objects.create(
                workspace=workspace,
                amount=opening_cash,
                entry_date=cutover_date,
                remarks=f"Migration Opening Balance Baseline ({cutover_date})",
                added_by=user,
            )

        logger.info(f"Initialized Cutover Baseline for workspace {workspace.public_id}: cash={opening_cash}, date={cutover_date}")
        return capital_entry

    @transaction.atomic
    def bulk_onboard_existing_borrowers(self, workspace: GuestWorkspace, borrower_data_list: list, user):
        """
        Imports active existing loans into CustomerProfile in a single atomic transaction.
        Calculates pre-digital collected amounts and sets outstanding balance accurately.
        """
        if not isinstance(borrower_data_list, list) or len(borrower_data_list) == 0:
            raise ValueError("Borrower data list cannot be empty.")

        created_customers = []
        total_loan_amount = Decimal("0.00")
        total_collected_pre_digital = Decimal("0.00")
        total_outstanding = Decimal("0.00")

        # Fetch lines map for quick lookup
        existing_lines = {str(l.public_id): l for l in CollectionLine.objects.filter(workspace=workspace)}

        # Determine base cutover date (from workspace's cutover capital entry or today)
        base_cutover_date = timezone.now().date()
        cutover_entry = CapitalEntry.objects.filter(
            workspace=workspace,
            remarks__icontains="Migration Opening Balance",
        ).first()
        if cutover_entry and cutover_entry.entry_date:
            base_cutover_date = cutover_entry.entry_date

        for item in borrower_data_list:
            full_name = str(item.get("full_name") or "").strip()
            if not full_name:
                continue

            mobile_number = str(item.get("mobile_number") or "").strip()
            loan_amount = Decimal(str(item.get("loan_amount") or item.get("disbursed_amount") or 0))
            installment_amount = Decimal(str(item.get("installment_amount") or 0))
            total_installments = int(item.get("total_installments") or 1)
            amount_already_collected = Decimal(str(item.get("amount_already_collected") or item.get("paid_amount") or 0))
            collection_day = str(item.get("collection_day") or "monday").lower()

            # Line lookup
            line_public_id = str(item.get("line_id") or item.get("line_public_id") or "")
            line_obj = existing_lines.get(line_public_id)

            # Calculation
            total_due = installment_amount * total_installments if installment_amount > 0 else loan_amount
            outstanding_balance = max(Decimal("0.00"), total_due - amount_already_collected)

            profit_amount = max(Decimal("0.00"), total_due - loan_amount)
            interest_rate = ((profit_amount / loan_amount) * Decimal("100.00")) if loan_amount > 0 else Decimal("0.00")

            paid_count = 0
            if installment_amount > 0 and amount_already_collected > 0:
                paid_count = min(int(amount_already_collected // installment_amount), total_installments)

            # Auto-calculate historical loan disbursement start_date going back to the past Nth collection weekday (e.g. 5th past Monday)
            DAY_NAME_TO_INT = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
            raw_start = item.get("start_date")
            if raw_start and str(raw_start).strip():
                start_date = str(raw_start)
            else:
                target_weekday = DAY_NAME_TO_INT.get(collection_day, 0)
                current_weekday = base_cutover_date.weekday()
                days_back = (current_weekday - target_weekday) % 7
                most_recent_collection_day = base_cutover_date - timedelta(days=days_back)

                if paid_count > 0:
                    disbursed_calc_date = most_recent_collection_day - timedelta(weeks=paid_count)
                else:
                    disbursed_calc_date = most_recent_collection_day

                start_date = str(disbursed_calc_date)

            status = CustomerStatus.CLOSED if outstanding_balance <= 0 else CustomerStatus.ACTIVE

            sequence_number = item.get("sequence_number")
            if sequence_number is not None:
                try:
                    sequence_number = int(sequence_number)
                except (ValueError, TypeError):
                    sequence_number = None

            # Customer code and sequence generation
            customer = CustomerService.create_customer(
                workspace=workspace,
                validated_data={
                    "sequence_number": sequence_number,
                    "full_name": full_name,
                    "mobile_number": mobile_number,
                    "line_id": line_obj.public_id if line_obj else None,
                    "collection_day": collection_day if collection_day in [c.value for c in CollectionDayChoices] else "monday",
                    "disbursed_amount": loan_amount,
                    "loan_amount": loan_amount,
                    "interest_rate": interest_rate,
                    "installment_amount": installment_amount,
                    "total_installments": total_installments,
                    "start_date": start_date,
                    "installments_paid_count": paid_count,
                    "outstanding_balance": outstanding_balance,
                    "status": status,
                    "remarks": f"Onboarded via Digital Migration (Pre-digital collected: Rs. {amount_already_collected})",
                },
                created_by=user,
            )

            # Ensure exact outstanding balance, paid count and calculated start_date are preserved
            customer.outstanding_balance = outstanding_balance
            customer.installments_paid_count = paid_count
            customer.start_date = start_date
            customer.status = status
            customer.save(update_fields=["outstanding_balance", "installments_paid_count", "start_date", "status", "updated_at"])

            created_customers.append(customer)
            total_loan_amount += loan_amount
            total_collected_pre_digital += amount_already_collected
            total_outstanding += outstanding_balance

        return {
            "imported_count": len(created_customers),
            "total_loan_amount": str(total_loan_amount),
            "total_collected_pre_digital": str(total_collected_pre_digital),
            "total_outstanding": str(total_outstanding),
            "customers": [
                {
                    "public_id": str(c.public_id),
                    "customer_code": c.customer_code,
                    "full_name": c.full_name,
                    "outstanding_balance": str(c.outstanding_balance),
                    "status": c.status,
                }
                for c in created_customers
            ],
        }

    @transaction.atomic
    def record_historical_lumpsum_adjustment(self, workspace: GuestWorkspace, amount: Decimal, category: str, remarks: str, user):
        """
        Records an optional historical lump-sum P&L adjustment entry.
        """
        amount = Decimal(str(amount or 0))
        remarks_full = f"Historical Migration Adjustment: {remarks or 'Pre-digital P&L adjustment'}"

        if category == "income":
            entry = CapitalEntry.objects.create(
                workspace=workspace,
                amount=amount,
                entry_date=timezone.now().date(),
                remarks=remarks_full,
                added_by=user,
            )
        else:
            from apps.masters.models import ExpenseCategory
            cat = ExpenseCategory.objects.first()
            entry = Expense.objects.create(
                workspace=workspace,
                amount=amount,
                expense_date=timezone.now().date(),
                category=cat,
                description=remarks_full,
                created_by=user,
            )

        return entry


onboarding_service = OnboardingService()
