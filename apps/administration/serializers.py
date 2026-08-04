"""
administration/serializers.py

Serializers for Super Admin endpoints.
"""

from rest_framework import serializers
from apps.guest_workspace.models import GuestWorkspace, SubscriptionPlan, WorkspaceStatus
from apps.administration.models import GlobalConfiguration, PromoCoupon, SubscriptionPlanConfig
from apps.accounts.models import User
from apps.common.validators import validate_mobile_number


class AdminWorkspaceListSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)
    owner_mobile = serializers.CharField(source="owner.mobile_number", read_only=True)
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    customer_count = serializers.IntegerField(read_only=True)

    allowed_collection_days = serializers.JSONField(read_only=True)
    configured_days_count = serializers.SerializerMethodField()
    max_collection_days = serializers.IntegerField(source="max_allowed_collection_days", read_only=True)
    purchased_additional_days = serializers.IntegerField(read_only=True)
    max_customers = serializers.IntegerField(source="max_allowed_customers", read_only=True)
    day_wise_customer_counts = serializers.SerializerMethodField()
    total_outstanding_amount = serializers.SerializerMethodField()

    class Meta:
        model = GuestWorkspace
        fields = [
            "public_id",
            "name",
            "owner_name",
            "owner_mobile",
            "owner_email",
            "address",
            "city",
            "state",
            "pin_code",
            "subscription_plan",
            "status",
            "max_customers_override",
            "max_collection_days_override",
            "allowed_collection_days",
            "configured_days_count",
            "max_collection_days",
            "purchased_additional_days",
            "max_customers",
            "customer_count",
            "day_wise_customer_counts",
            "total_outstanding_amount",
            "created_at",
        ]

    def get_configured_days_count(self, obj):
        return len(obj.allowed_collection_days or [])

    def get_day_wise_customer_counts(self, obj):
        from apps.guest_workspace.models import CustomerProfile
        from django.db.models import Count

        counts = (
            CustomerProfile.objects.filter(workspace=obj)
            .values("collection_day")
            .annotate(count=Count("id"))
        )
        day_map = {
            "monday": 0,
            "tuesday": 0,
            "wednesday": 0,
            "thursday": 0,
            "friday": 0,
            "saturday": 0,
            "sunday": 0,
            "unassigned": 0,
        }
        for item in counts:
            day = (item["collection_day"] or "unassigned").lower().strip()
            if day in day_map:
                day_map[day] = item["count"]
            else:
                day_map["unassigned"] += item["count"]
        return day_map

    def get_total_outstanding_amount(self, obj):
        from apps.guest_workspace.models import CustomerProfile
        from django.db.models import Sum
        val = CustomerProfile.objects.filter(workspace=obj).aggregate(total=Sum("outstanding_balance"))["total"]
        return float(val or 0)


class AdminLenderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    mobile_number = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(min_length=6, write_only=True)
    workspace_name = serializers.CharField(max_length=200)
    address = serializers.CharField(required=False, allow_blank=True, default="")
    city = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    state = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    pin_code = serializers.CharField(max_length=10, required=False, allow_blank=True, default="")
    subscription_plan = serializers.ChoiceField(choices=SubscriptionPlan.choices, default=SubscriptionPlan.FREE)
    status = serializers.ChoiceField(choices=WorkspaceStatus.choices, default=WorkspaceStatus.ACTIVE)
    max_customers_override = serializers.IntegerField(required=False, allow_null=True)
    max_collection_days_override = serializers.IntegerField(required=False, allow_null=True)

    def validate_subscription_plan(self, value):
        if value in ["guest", "free"]:
            return "free"
        return value

    def validate_mobile_number(self, value):
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            value = validate_mobile_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(str(exc.message if hasattr(exc, 'message') else exc))
        except Exception as exc:
            raise serializers.ValidationError(str(exc))

        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return value


class AdminLenderUpdateSerializer(serializers.Serializer):
    owner_name = serializers.CharField(max_length=150, required=False)
    owner_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    owner_mobile = serializers.CharField(max_length=15, required=False)
    name = serializers.CharField(max_length=200, required=False)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pin_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    subscription_plan = serializers.ChoiceField(choices=SubscriptionPlan.choices, required=False)
    status = serializers.ChoiceField(choices=WorkspaceStatus.choices, required=False)
    max_customers_override = serializers.IntegerField(required=False, allow_null=True)
    max_collection_days_override = serializers.IntegerField(required=False, allow_null=True)


class AdminLenderPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6)


class QuotaOverrideSerializer(serializers.Serializer):
    max_customers_override = serializers.IntegerField(required=False, allow_null=True)
    max_collection_days_override = serializers.IntegerField(required=False, allow_null=True)


class WorkspaceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["active", "suspended", "read_only"])


class GlobalConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalConfiguration
        fields = ["id", "key", "value", "description", "is_active", "updated_at"]


class PromoCouponSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateTimeField(required=False, allow_null=True)
    valid_until = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = PromoCoupon
        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "max_uses",
            "used_count",
            "valid_from",
            "valid_until",
            "is_active",
            "created_at",
        ]


class BroadcastNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=["info", "warning", "upgrade", "maintenance"], default="info"
    )
    target_plan = serializers.ChoiceField(
        choices=["all", "free", "premium"], default="all"
    )


class AdminSubscriptionSummarySerializer(serializers.Serializer):
    total_active = serializers.IntegerField()
    total_trials = serializers.IntegerField()
    total_cancelled = serializers.IntegerField()
    monthly_recurring_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    annual_recurring_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    workspaces = AdminWorkspaceListSerializer(many=True)


class AdminInvoiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    workspace_name = serializers.CharField()
    plan = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    issue_date = serializers.CharField()
    due_date = serializers.CharField()


class SubscriptionPlanConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlanConfig
        fields = [
            "id",
            "plan_code",
            "target_user_type",
            "name",
            "monthly_price",
            "annual_price",
            "tagline",
            "max_customers",
            "max_collection_days",
            "additional_days",
            "features",
            "is_popular",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
