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
            "customer_count",
            "created_at",
        ]


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
