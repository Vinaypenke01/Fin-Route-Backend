"""
guest_workspace/services/collection_service.py

CollectionService handles all collection recording business logic:
- Plan limit enforcement (collection day quota)
- Single and batch collection recording
- Balance updates on CustomerProfile
- Collection CRUD
"""

import logging
from datetime import date as date_type
from django.db import transaction

from apps.common.exceptions import CollectionNotFoundException, BusinessRuleException
from apps.common.utils import generate_receipt_number
from apps.guest_workspace.models import CollectionEntry, GuestWorkspace, CustomerProfile
from apps.guest_workspace.services.workspace_service import GuestWorkspaceService
from apps.guest_workspace.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class CollectionService:
    """
    Handles collection recording, plan limit enforcement, and balance updates.

    Critical rules:
    - check_collection_day_limit() MUST be called before every new collection.
    - outstanding_balance MUST be recalculated after every collection save.
    - Batch collections are atomic — all succeed or all fail.
    """

    @staticmethod
    @transaction.atomic
    def record_collection(
        workspace: GuestWorkspace,
        validated_data: dict,
        collected_by,
    ) -> CollectionEntry:
        """
        Record a single collection entry.

        Steps:
        1. Check collection day quota.
        2. Auto-generate receipt number.
        3. Save CollectionEntry.
        4. Recalculate customer outstanding balance.

        Returns:
            Newly created CollectionEntry.
        """
        collection_date = validated_data.pop("collection_date", date_type.today())

        # Enforce plan limits
        GuestWorkspaceService.check_collection_day_quota(workspace, collection_date)

        # Get customer (scoped to workspace)
        customer_id = validated_data.pop("customer_id", None)
        customer_public_id = validated_data.pop("customer", None)

        if customer_id:
            try:
                customer = CustomerProfile.objects.get(id=customer_id, workspace=workspace)
            except CustomerProfile.DoesNotExist:
                raise BusinessRuleException("Customer not found in this workspace.")
        else:
            customer = CustomerService.get_customer_detail(workspace, str(customer_public_id))        # Extract FK integer IDs safely (avoid "must be a X instance" errors)
        raw_status = validated_data.pop("status", None)
        status_id = int(raw_status) if raw_status is not None else None

        raw_mode = validated_data.pop("payment_mode", None)
        mode_id = int(raw_mode) if raw_mode is not None else None

        # If status is skipped, force collected_amount to 0 and payment_mode to None
        from apps.masters.models import CollectionStatus
        if status_id:
            try:
                st = CollectionStatus.objects.get(id=status_id)
                if st.code == "skipped":
                    validated_data["collected_amount"] = 0
                    mode_id = None
            except CollectionStatus.DoesNotExist:
                pass

        receipt = generate_receipt_number(workspace.id, collection_date)

        collection = CollectionEntry.objects.create(
            workspace=workspace,
            customer=customer,
            collected_by=collected_by,
            receipt_number=receipt,
            collection_date=collection_date,
            status_id=status_id,
            payment_mode_id=mode_id,
            **validated_data,
        )

        # Update customer balance and installment counters
        CustomerService.recalculate_outstanding(customer)

        logger.info(
            "Collection recorded: receipt=%s customer=%s amount=%s collected_by=%s",
            receipt,
            customer.customer_code,
            collection.collected_amount,
            getattr(collected_by, "username", str(collected_by)),
        )
        return collection

    @staticmethod
    @transaction.atomic
    def record_batch_collections(
        workspace: GuestWorkspace,
        collection_date: date_type,
        entries: list,
        collected_by,
    ) -> list:
        """
        Record multiple collection entries for a single date in one atomic transaction.

        Args:
            workspace: The workspace context.
            collection_date: The date for all entries.
            entries: List of dicts with customer_public_id, collected_amount, status, payment_mode.
            collected_by: The user recording the collections.

        Returns:
            List of created CollectionEntry instances.

        Raises:
            PlanLimitExceededException if the date exceeds the weekly limit.
            Rolls back ALL entries if any single entry fails.
        """
        # Check limit once for the whole batch
        GuestWorkspaceService.check_collection_day_quota(workspace, collection_date)

        from apps.masters.models import CollectionStatus

        created = []
        for entry_data in entries:
            # Each entry still goes through record_collection minus limit check
            customer_public_id = entry_data.get("customer")
            customer = CustomerService.get_customer_detail(workspace, str(customer_public_id))

            status_id = entry_data.get("status")
            mode_id = entry_data.get("payment_mode")
            collected_amount = entry_data.get("collected_amount", 0)

            if status_id:
                try:
                    st = CollectionStatus.objects.get(id=status_id)
                    if st.code == "skipped":
                        collected_amount = 0
                        mode_id = None
                except CollectionStatus.DoesNotExist:
                    pass

            receipt = generate_receipt_number(workspace.id, collection_date)
            collection = CollectionEntry.objects.create(
                workspace=workspace,
                customer=customer,
                collected_by=collected_by,
                collection_date=collection_date,
                receipt_number=receipt,
                expected_amount=entry_data.get("expected_amount", 0),
                collected_amount=collected_amount,
                status_id=status_id,
                payment_mode_id=mode_id,
                remarks=entry_data.get("remarks", ""),
                is_collected_today=entry_data.get("is_collected_today", True),
            )
            CustomerService.recalculate_outstanding(customer)

        logger.info(
            "Batch collection recorded: %d entries for workspace=%s date=%s",
            len(created),
            workspace.name,
            collection_date,
        )
        return created

    @staticmethod
    def get_collections(workspace: GuestWorkspace, filters: dict = None):
        """
        Return paginated collection entries for a workspace with optional filters.

        Supported filters:
        - date_from / date_to
        - customer (public_id)
        - status
        - payment_mode
        """
        queryset = CollectionEntry.objects.filter(
            workspace=workspace
        ).select_related("customer", "status", "payment_mode", "collected_by")

        if filters:
            if date_from := filters.get("date_from"):
                queryset = queryset.filter(collection_date__gte=date_from)
            if date_to := filters.get("date_to"):
                queryset = queryset.filter(collection_date__lte=date_to)
            if customer_id := filters.get("customer"):
                queryset = queryset.filter(customer__public_id=customer_id)
            if status := filters.get("status"):
                queryset = queryset.filter(status__code=status)
            if payment_mode := filters.get("payment_mode"):
                queryset = queryset.filter(payment_mode__code=payment_mode)

        return queryset

    @staticmethod
    def get_collection_detail(
        workspace: GuestWorkspace,
        collection_public_id: str,
    ) -> CollectionEntry:
        """
        Return a single collection entry by public_id, scoped to workspace.

        Raises:
            CollectionNotFoundException if not found.
        """
        try:
            return CollectionEntry.objects.select_related(
                "customer", "status", "payment_mode"
            ).get(public_id=collection_public_id, workspace=workspace)
        except CollectionEntry.DoesNotExist:
            raise CollectionNotFoundException()

    @staticmethod
    @transaction.atomic
    def update_collection(
        workspace: GuestWorkspace,
        collection_public_id: str,
        validated_data: dict,
    ) -> CollectionEntry:
        """Update a collection entry and recalculate the customer balance."""
        collection = CollectionService.get_collection_detail(workspace, collection_public_id)

        allowed_fields = ["collected_amount", "status", "payment_mode", "remarks"]
        for field in allowed_fields:
            if field in validated_data:
                setattr(collection, field, validated_data[field])
        collection.save()

        CustomerService.recalculate_outstanding(collection.customer)
        return collection

    @staticmethod
    @transaction.atomic
    def delete_collection(workspace: GuestWorkspace, collection_public_id: str) -> None:
        """Delete a collection entry and recalculate the customer balance."""
        collection = CollectionService.get_collection_detail(workspace, collection_public_id)
        customer = collection.customer
        collection.delete()
        CustomerService.recalculate_outstanding(customer)
        logger.info("Collection deleted: %s", collection_public_id)
