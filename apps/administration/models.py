"""
administration/models.py

Models for the Super Admin Console (`/admin/*` screens):
- GlobalConfiguration: Platform-wide configuration & feature flags
- PromoCoupon: Discounts and coupons for subscriptions
- SubscriptionPlanConfig: Dynamic plan catalog, pricing & quotas
"""

from django.db import models
from apps.common.models import BaseModel


class DiscountType(models.TextChoices):
    FLAT = "flat", "Flat Amount (₹)"
    PERCENTAGE = "percentage", "Percentage (%)"


class GlobalConfiguration(BaseModel):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Global Configuration"
        verbose_name_plural = "Global Configurations"

    def __str__(self):
        return f"{self.key} = {self.value}"


class PromoCoupon(BaseModel):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Promo Coupon"
        verbose_name_plural = "Promo Coupons"

    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.discount_value})"


class PlanTargetType(models.TextChoices):
    GUEST = "guest", "Guest User (Collection Day Add-ons)"
    LENDER = "lender", "Full ERP Lender (Institutional / Company)"


class SubscriptionPlanConfig(BaseModel):
    """
    Super Admin configurable subscription plan catalog & pricing configuration.
    """

    plan_code = models.CharField(max_length=50, unique=True, db_index=True)
    target_user_type = models.CharField(
        max_length=20,
        choices=PlanTargetType.choices,
        default=PlanTargetType.GUEST,
        db_index=True,
        help_text="Target category: guest (day-based add-ons) or lender (full institutional ERP).",
    )
    name = models.CharField(max_length=150)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tagline = models.CharField(max_length=255, blank=True, default="")
    max_customers = models.IntegerField(default=50, help_text="0 for unlimited")
    max_collection_days = models.IntegerField(default=7)
    additional_days = models.IntegerField(default=1, help_text="Additional collection days granted by this plan (e.g. 1 for +1 day, 2 for +2 days).")
    features = models.JSONField(default=list, blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Subscription Plan Configuration"
        verbose_name_plural = "Subscription Plan Configurations"
        ordering = ["sort_order", "monthly_price"]

    def __str__(self):
        return f"{self.name} ({self.plan_code}) - ₹{self.monthly_price}/mo"


class UpgradeRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending Verification"
    APPROVED = "approved", "Approved & Activated"
    REJECTED = "rejected", "Rejected"


class PlanUpgradeRequest(BaseModel):
    """
    Stores plan upgrade requests initiated by guest lenders via the Upgrade screen / WhatsApp flow.
    Super Admins can review, approve, or reject requests.
    """

    workspace = models.ForeignKey(
        "guest_workspace.GuestWorkspace",
        on_delete=models.CASCADE,
        related_name="upgrade_requests",
    )
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="upgrade_requests",
    )
    plan_code = models.CharField(max_length=50)
    plan_name = models.CharField(max_length=150)
    additional_days = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=UpgradeRequestStatus.choices,
        default=UpgradeRequestStatus.PENDING,
        db_index=True,
    )
    admin_notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Plan Upgrade Request"
        verbose_name_plural = "Plan Upgrade Requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.workspace.name} - {self.plan_name} ({self.status})"

