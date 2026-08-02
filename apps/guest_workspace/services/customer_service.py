"""
guest_workspace/services/customer_service.py

CustomerService handles all customer CRUD and balance management.
"""

import logging
from django.db import transaction

from apps.common.exceptions import CustomerNotFoundException, BusinessRuleException
from apps.common.utils import generate_customer_code
from apps.guest_workspace.models import CustomerProfile, GuestWorkspace, CustomerStatus
from apps.guest_workspace.services.workspace_service import GuestWorkspaceService

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Manages customer lifecycle within a Guest Workspace.

    Rules:
    - Quota is checked before every new customer creation.
    - customer_code is auto-generated and unique across the platform.
    - outstanding_balance is updated after every collection.
    - Deletion is soft (status = suspended) for audit trail.
    """

    @staticmethod
    @transaction.atomic
    def create_customer(workspace: GuestWorkspace, validated_data: dict, created_by) -> CustomerProfile:
        """
        Create a new customer in the workspace.

        Steps:
        1. Check workspace customer quota.
        2. Auto-generate customer_code.
        3. Create CustomerProfile.
        4. Calculate initial total_due and outstanding_balance.

        Returns:
            Newly created CustomerProfile.
        """
        GuestWorkspaceService.check_customer_quota(workspace)

        # Auto-generate customer code
        existing_count = CustomerProfile.objects.filter(workspace=workspace).count()
        customer_code = generate_customer_code(workspace.id, existing_count + 1)

        # Calculate total due from loan amount and interest
        loan_amount = validated_data.get("loan_amount", 0)
        interest_rate = validated_data.get("interest_rate", 0)
        total_due = CustomerService._calculate_total_due(
            loan_amount=loan_amount,
            interest_rate=float(interest_rate),
            interest_type=validated_data.get("interest_type"),
        )

        collection_frequency_val = validated_data.pop("collection_frequency", None)
        if isinstance(collection_frequency_val, int) or (isinstance(collection_frequency_val, str) and str(collection_frequency_val).isdigit()):
            collection_frequency_id = int(collection_frequency_val)
        elif hasattr(collection_frequency_val, "id"):
            collection_frequency_id = collection_frequency_val.id
        else:
            collection_frequency_id = collection_frequency_val or 1

        interest_type_val = validated_data.pop("interest_type", None)
        if isinstance(interest_type_val, int) or (isinstance(interest_type_val, str) and str(interest_type_val).isdigit()):
            interest_type_id = int(interest_type_val)
        elif hasattr(interest_type_val, "id"):
            interest_type_id = interest_type_val.id
        else:
            interest_type_id = interest_type_val or 1

        is_existing_borrower = validated_data.get("is_existing_borrower", False)
        amount_already_collected = validated_data.get("amount_already_collected", 0) or 0
        installments_paid_count = validated_data.get("installments_paid_count", 0) or 0
        remaining_installments_count = validated_data.get("remaining_installments_count", 1) or 1
        total_installments = validated_data.get("total_installments") or (installments_paid_count + remaining_installments_count if is_existing_borrower else remaining_installments_count)

        installment_amount = validated_data.get("installment_amount")
        if not installment_amount or float(installment_amount) <= 0:
            installment_amount = (float(total_due) / total_installments) if total_installments > 0 else 0.0

        outstanding_balance = max(0.0, float(total_due) - float(amount_already_collected))

        customer = CustomerProfile.objects.create(
            workspace=workspace,
            customer_code=customer_code,
            created_by=created_by,
            collection_frequency_id=collection_frequency_id,
            interest_type_id=interest_type_id,
            total_due=total_due,
            outstanding_balance=outstanding_balance,
            is_existing_borrower=is_existing_borrower,
            total_installments=total_installments,
            installments_paid_count=installments_paid_count,
            remaining_installments_count=remaining_installments_count,
            amount_already_collected=amount_already_collected,
            installment_amount=installment_amount,
            notes=validated_data.get("notes") or (f"Imported ongoing loan: {installments_paid_count} paid, {remaining_installments_count} remaining, ₹{amount_already_collected} collected" if is_existing_borrower else ""),
            **{k: v for k, v in validated_data.items()
               if k not in ("total_due", "outstanding_balance", "is_existing_borrower", "total_installments", "installments_paid_count", "remaining_installments_count", "amount_already_collected", "installment_amount", "notes", "collection_frequency", "interest_type")},
        )

        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType
        AuditLogService.log_action(
            user=created_by or workspace.owner,
            action=ActionType.CREATE,
            target_model="CustomerProfile",
            target_id=str(customer.public_id),
            description=f"Added new borrower '{customer.full_name}' ({customer.customer_code}) with loan amount ₹{customer.loan_amount}",
        )

        logger.info(
            "Customer created: code=%s workspace=%s",
            customer_code,
            workspace.name,
        )

        if is_existing_borrower and float(amount_already_collected) > 0:
            try:
                from datetime import date as date_type, timedelta
                from apps.guest_workspace.models import CollectionEntry
                from apps.guest_workspace.services.collection_service import generate_receipt_number
                from apps.masters.models import CollectionStatus, PaymentMode

                coll_date = customer.start_date or (date_type.today() - timedelta(days=1))
                status_obj = CollectionStatus.objects.filter(code="paid").first()
                mode_obj = PaymentMode.objects.first()

                CollectionEntry.objects.create(
                    workspace=workspace,
                    customer=customer,
                    collected_by=created_by,
                    receipt_number=generate_receipt_number(workspace.id, coll_date),
                    collection_date=coll_date,
                    expected_amount=amount_already_collected,
                    collected_amount=amount_already_collected,
                    status_id=status_obj.id if status_obj else 1,
                    payment_mode_id=mode_obj.id if mode_obj else 1,
                    remarks=f"Initial opening balance record for existing borrower ({installments_paid_count} past installments paid)",
                )
            except Exception as e:
                logger.error("Failed to create initial collection entry for existing borrower: %s", e)

        return customer

    @staticmethod
    def get_customer_list(workspace: GuestWorkspace, filters: dict = None):
        """
        Return paginated customers for a workspace with optional filters.

        Supported filters:
        - status (active/closed/defaulted/suspended)
        - search (full_name, mobile_number, customer_code)
        - collection_frequency
        - ordering
        """
        queryset = CustomerProfile.objects.filter(workspace=workspace).select_related(
            "collection_frequency", "interest_type"
        )

        if filters:
            status = filters.get("status")
            if status and str(status).lower() not in ("all", "undefined", "null", ""):
                queryset = queryset.filter(status=status)

            search = filters.get("search")
            if search and str(search).lower() not in ("undefined", "null", ""):
                q_filter = (
                    models.Q(full_name__icontains=search)
                    | models.Q(mobile_number__icontains=search)
                    | models.Q(customer_code__icontains=search)
                )
                if str(search).strip().isdigit():
                    q_filter |= models.Q(sequence_number=int(search.strip()))
                queryset = queryset.filter(q_filter)

            freq = filters.get("collection_frequency")
            if freq and str(freq).lower() not in ("all", "undefined", "null", ""):
                queryset = queryset.filter(collection_frequency__code=freq)

            collection_day = filters.get("collection_day")
            if collection_day and str(collection_day).lower() not in ("all", "undefined", "null", ""):
                queryset = queryset.filter(collection_day=str(collection_day).lower())

        results = list(queryset.order_by("sequence_number", "customer_code"))
        for cust in results:
            CustomerService.recalculate_outstanding(cust)
        return results

    @staticmethod
    def get_customer_detail(workspace: GuestWorkspace, customer_public_id: str) -> CustomerProfile:
        """
        Return a single customer by public_id, scoped to the workspace.

        Raises:
            CustomerNotFoundException if not found.
        """
        try:
            cust = CustomerProfile.objects.select_related(
                "collection_frequency", "interest_type", "workspace"
            ).get(public_id=customer_public_id, workspace=workspace)
            CustomerService.recalculate_outstanding(cust)
            cust.refresh_from_db()
            return cust
        except CustomerProfile.DoesNotExist:
            raise CustomerNotFoundException()

    @staticmethod
    @transaction.atomic
    def update_customer(
        workspace: GuestWorkspace,
        customer_public_id: str,
        validated_data: dict,
    ) -> CustomerProfile:
        """Update a customer's profile fields."""
        customer = CustomerService.get_customer_detail(workspace, customer_public_id)

        collection_frequency_val = validated_data.pop("collection_frequency", None)
        if collection_frequency_val is not None:
            if isinstance(collection_frequency_val, int) or (isinstance(collection_frequency_val, str) and str(collection_frequency_val).isdigit()):
                customer.collection_frequency_id = int(collection_frequency_val)
            elif hasattr(collection_frequency_val, "id"):
                customer.collection_frequency_id = collection_frequency_val.id

        interest_type_val = validated_data.pop("interest_type", None)
        if interest_type_val is not None:
            if isinstance(interest_type_val, int) or (isinstance(interest_type_val, str) and str(interest_type_val).isdigit()):
                customer.interest_type_id = int(interest_type_val)
            elif hasattr(interest_type_val, "id"):
                customer.interest_type_id = interest_type_val.id

        # Recalculate total_due if loan financial parameters are edited
        if "loan_amount" in validated_data or "interest_rate" in validated_data or interest_type_val is not None:
            loan_amount = validated_data.get("loan_amount", customer.loan_amount)
            interest_rate = validated_data.get("interest_rate", customer.interest_rate)
            customer.total_due = CustomerService._calculate_total_due(
                loan_amount=loan_amount,
                interest_rate=float(interest_rate),
                interest_type=customer.interest_type_id,
            )

        for field, value in validated_data.items():
            setattr(customer, field, value)

        customer.save()
        CustomerService.recalculate_outstanding(customer)
        return customer

    @staticmethod
    @transaction.atomic
    def delete_customer(workspace: GuestWorkspace, customer_public_id: str) -> None:
        """Permanently delete a customer profile."""
        customer = CustomerService.get_customer_detail(workspace, customer_public_id)
        customer.delete()

    @staticmethod
    @transaction.atomic
    def archive_customer(workspace: GuestWorkspace, customer_public_id: str) -> CustomerProfile:
        """
        Archive (soft-close) a customer.
        A customer can be archived when outstanding_balance = 0.
        """
        customer = CustomerService.get_customer_detail(workspace, customer_public_id)

        if float(customer.outstanding_balance) > 0:
            raise BusinessRuleException(
                f"Cannot close customer with outstanding balance of ₹{customer.outstanding_balance}."
            )

        customer.status = CustomerStatus.CLOSED
        customer.save(update_fields=["status", "updated_at"])
        return customer

    @staticmethod
    @transaction.atomic
    def recalculate_outstanding(customer: CustomerProfile) -> None:
        """
        Recalculate the outstanding balance and paid installment counters.
        Called by CollectionService after every collection event.
        """
        from django.db.models import Sum
        paid_qs = customer.collections.filter(status__affects_outstanding=True)

        # Exclude opening balance entries from regular collection count
        regular_collections_qs = paid_qs.exclude(remarks__icontains="initial opening")
        new_regular_collections_count = regular_collections_qs.count()

        # Calculate total collected from regular collections
        regular_paid_total = regular_collections_qs.aggregate(total=Sum("collected_amount"))["total"] or 0
        opening_collected = float(customer.amount_already_collected or 0)

        # Calculate initial paid installments from amount_already_collected / installment_amount or initial record
        total_installments = customer.total_installments or 20
        inst_amt = float(customer.installment_amount or 0)

        if customer.is_existing_borrower and inst_amt > 0 and opening_collected > 0:
            initial_paid = int(round(opening_collected / inst_amt))
        else:
            initial_paid = 0

        effective_paid_count = min(total_installments, initial_paid + new_regular_collections_count)
        remaining_count = max(0, total_installments - effective_paid_count)

        new_balance = max(0.0, float(customer.total_due) - opening_collected - float(regular_paid_total))

        CustomerProfile.objects.filter(pk=customer.pk).update(
            outstanding_balance=new_balance,
            installments_paid_count=effective_paid_count,
            remaining_installments_count=remaining_count,
        )

    @staticmethod
    def _calculate_total_due(
        loan_amount: float,
        interest_rate: float,
        interest_type,
    ) -> float:
        """
        Calculate total repayable amount based on interest type.
        Supports InterestType model instance, code string, or integer PK ID.
        """
        if not interest_type:
            return float(loan_amount)

        code = None
        if hasattr(interest_type, "code"):
            code = interest_type.code
        elif isinstance(interest_type, int) or (isinstance(interest_type, str) and str(interest_type).isdigit()):
            from apps.masters.models import InterestType
            itype = InterestType.objects.filter(pk=int(interest_type)).first()
            if itype:
                code = itype.code
        else:
            code = str(interest_type)

        if code in ("flat_percentage", "flat", "monthly_percentage"):
            return round(float(loan_amount) * (1 + float(interest_rate) / 100), 2)
        elif code in ("fixed_amount", "fixed"):
            return round(float(loan_amount) + float(interest_rate), 2)
        else:
            return float(loan_amount)


# Needed for Q objects in get_customer_list
from django.db import models  # noqa: E402
