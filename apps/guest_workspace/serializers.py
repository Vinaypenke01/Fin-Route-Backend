"""
guest_workspace/serializers.py

Serializers for Guest Workspace models:
- Workspace
- Customer
- Collection (Single & Batch)
- Expense
- Calculator
"""

from rest_framework import serializers
from apps.common.validators import validate_mobile_number, validate_positive_amount
from apps.guest_workspace.models import (
    GuestWorkspace,
    CustomerProfile,
    CollectionEntry,
    Expense,
    CustomerStatus,
)


# ─── Workspace Serializers ───────────────────────────────────────────────────

class GuestWorkspaceSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    business_category_name = serializers.CharField(source="business_category.name", read_only=True)
    max_allowed_collection_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = GuestWorkspace
        fields = [
            "public_id",
            "name",
            "business_category",
            "business_category_name",
            "mobile_number",
            "gstin",
            "business_type",
            "owner_pan",
            "logo",
            "address",
            "city",
            "state",
            "pin_code",
            "subscription_plan",
            "status",
            "allowed_collection_days",
            "max_allowed_collection_days",
            "created_at",
        ]
        read_only_fields = ["public_id", "subscription_plan", "status", "max_allowed_collection_days", "created_at"]


class PlanUpgradeRequestSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    lender_name = serializers.CharField(source="requested_by.full_name", read_only=True)
    lender_mobile = serializers.CharField(source="requested_by.mobile_number", read_only=True)

    class Meta:
        from apps.administration.models import PlanUpgradeRequest
        model = PlanUpgradeRequest
        fields = [
            "id",
            "workspace_name",
            "lender_name",
            "lender_mobile",
            "plan_code",
            "plan_name",
            "additional_days",
            "amount",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class GuestWorkspaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestWorkspace
        fields = [
            "name",
            "business_category",
            "mobile_number",
            "gstin",
            "business_type",
            "owner_pan",
            "logo",
            "address",
            "city",
            "state",
            "pin_code",
            "allowed_collection_days",
        ]


# ─── Customer Serializers ─────────────────────────────────────────────────────

class CustomerProfileListSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    collection_frequency_name = serializers.CharField(source="collection_frequency.name", read_only=True)
    interest_type_name = serializers.CharField(source="interest_type.name", read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            "public_id",
            "customer_code",
            "sequence_number",
            "full_name",
            "mobile_number",
            "loan_amount",
            "disbursed_amount",
            "interest_rate",
            "total_due",
            "outstanding_balance",
            "collection_frequency",
            "collection_frequency_name",
            "collection_day",
            "interest_type",
            "interest_type_name",
            "is_existing_borrower",
            "total_installments",
            "installments_paid_count",
            "remaining_installments_count",
            "amount_already_collected",
            "installment_amount",
            "status",
            "start_date",
        ]


class CustomerProfileDetailSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            "public_id",
            "customer_code",
            "sequence_number",
            "full_name",
            "mobile_number",
            "alternate_mobile",
            "photo",
            "id_proof_type",
            "id_proof_number",
            "address",
            "city",
            "state",
            "pin_code",
            "collection_frequency",
            "collection_day",
            "interest_type",
            "interest_rate",
            "loan_amount",
            "disbursed_amount",
            "total_due",
            "outstanding_balance",
            "is_existing_borrower",
            "total_installments",
            "installments_paid_count",
            "remaining_installments_count",
            "amount_already_collected",
            "installment_amount",
            "start_date",
            "end_date",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["public_id", "customer_code", "total_due", "outstanding_balance", "created_at"]


class CustomerCreateUpdateSerializer(serializers.Serializer):
    sequence_number = serializers.IntegerField(required=False, allow_null=True)
    full_name = serializers.CharField(max_length=200)
    mobile_number = serializers.CharField(max_length=15)
    alternate_mobile = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pin_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    id_proof_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    id_proof_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    collection_frequency = serializers.IntegerField(help_text="CollectionFrequency PK ID")
    collection_day = serializers.CharField(max_length=20, required=False, default="monday")
    interest_type = serializers.IntegerField(help_text="InterestType PK ID")
    interest_rate = serializers.DecimalField(max_digits=8, decimal_places=4)
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    disbursed_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    is_existing_borrower = serializers.BooleanField(required=False, default=False)
    total_installments = serializers.IntegerField(required=False, default=1)
    installments_paid_count = serializers.IntegerField(required=False, default=0)
    remaining_installments_count = serializers.IntegerField(required=False, default=1)
    amount_already_collected = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    installment_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)

    def validate_mobile_number(self, value):
        return validate_mobile_number(value)

    def validate(self, attrs):
        validate_positive_amount(attrs["loan_amount"])
        validate_positive_amount(attrs["disbursed_amount"])
        return attrs


# ─── Collection Serializers ───────────────────────────────────────────────────

class CollectionListSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    customer_code = serializers.CharField(source="customer.customer_code", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_public_id = serializers.UUIDField(source="customer.public_id", read_only=True)
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    payment_mode_name = serializers.CharField(source="payment_mode.name", read_only=True)
    is_collected_today = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = CollectionEntry
        fields = [
            "public_id",
            "receipt_number",
            "customer_code",
            "customer_name",
            "customer_public_id",
            "collection_date",
            "expected_amount",
            "collected_amount",
            "status",
            "status_code",
            "status_name",
            "payment_mode",
            "payment_mode_name",
            "remarks",
            "is_collected_today",
            "created_at",
        ]


class CollectionCreateSerializer(serializers.Serializer):
    customer = serializers.UUIDField(help_text="Customer public_id UUID")
    collection_date = serializers.DateField()
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    collected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.IntegerField(help_text="CollectionStatus PK ID")
    payment_mode = serializers.IntegerField(required=False, allow_null=True, help_text="PaymentMode PK ID")
    remarks = serializers.CharField(required=False, allow_blank=True)
    is_collected_today = serializers.BooleanField(required=False, default=True)

    def validate(self, attrs):
        validate_positive_amount(attrs["collected_amount"])
        return attrs


class SingleBatchEntrySerializer(serializers.Serializer):
    customer = serializers.UUIDField(help_text="Customer public_id UUID")
    expected_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    collected_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.IntegerField(help_text="CollectionStatus PK ID")
    payment_mode = serializers.IntegerField(required=False, allow_null=True, help_text="PaymentMode PK ID")
    remarks = serializers.CharField(required=False, allow_blank=True)
    is_collected_today = serializers.BooleanField(required=False, default=True)


class BatchCollectionSerializer(serializers.Serializer):
    collection_date = serializers.DateField()
    entries = SingleBatchEntrySerializer(many=True)


# ─── Expense Serializers ──────────────────────────────────────────────────────

class ExpenseListSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    payment_mode_name = serializers.CharField(source="payment_mode.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "public_id",
            "category",
            "category_name",
            "amount",
            "expense_date",
            "description",
            "payment_mode",
            "payment_mode_name",
            "receipt_image",
            "created_at",
        ]


class ExpenseCreateSerializer(serializers.Serializer):
    category = serializers.IntegerField(help_text="ExpenseCategory PK ID")
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True)
    payment_mode = serializers.IntegerField(required=False, allow_null=True)

    def validate_amount(self, value):
        validate_positive_amount(value)
        return value


# ─── Calculator Serializers ───────────────────────────────────────────────────

class CalculatorRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=8, decimal_places=4)
    interest_type = serializers.ChoiceField(
        choices=["flat_percentage", "fixed_amount", "monthly_percentage"]
    )
    frequency = serializers.ChoiceField(choices=["daily", "weekly", "monthly"])
    duration = serializers.IntegerField(min_value=1, max_value=365)
    start_date = serializers.DateField(required=False, allow_null=True)
