"""
masters/models.py

Reference data / Master tables for the platform.

Includes:
- Location tables: State, District, City, Village, PostalLocation
- Domain master tables: CollectionFrequency, InterestType, PaymentMode, CollectionStatus, ExpenseCategory, BusinessCategory
"""

from django.db import models
from apps.common.models import BaseModel, BasePublicModel


# ─── Location Data ────────────────────────────────────────────────────────────

class State(BasePublicModel):
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=10, db_index=True)
    country_code = models.CharField(max_length=5, default="IN", db_index=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=50, default="system")
    external_id = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class District(BasePublicModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ["name"]
        unique_together = ["state", "name"]

    def __str__(self):
        return f"{self.name}, {self.state.code}"


class City(BasePublicModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100, db_index=True)
    location_type = models.CharField(max_length=50, default="city")  # city, town, municipality
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class Village(BasePublicModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="villages")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="villages")
    name = models.CharField(max_length=100, db_index=True)
    postal_code = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "Village"
        verbose_name_plural = "Villages"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class PostalLocation(BaseModel):
    postal_code = models.CharField(max_length=10, db_index=True)
    post_office_name = models.CharField(max_length=150)
    branch_type = models.CharField(max_length=50, blank=True)
    district_name = models.CharField(max_length=100, blank=True)
    state_name = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        verbose_name = "Postal Location"
        verbose_name_plural = "Postal Locations"
        indexes = [models.Index(fields=["postal_code"])]

    def __str__(self):
        return f"{self.postal_code} — {self.post_office_name} ({self.district_name})"


# ─── Domain Master Tables ─────────────────────────────────────────────────────

class CollectionFrequency(BaseModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)  # daily, weekly, monthly
    name = models.CharField(max_length=50)  # Daily, Weekly, Monthly
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Collection Frequency"
        verbose_name_plural = "Collection Frequencies"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class InterestType(BaseModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)  # flat_percentage, fixed_amount, etc.
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Interest Type"
        verbose_name_plural = "Interest Types"
        ordering = ["id"]

    def __str__(self):
        return self.name


class PaymentMode(BaseModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)  # cash, upi, bank_transfer, cheque, other
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Payment Mode"
        verbose_name_plural = "Payment Modes"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class CollectionStatus(BaseModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)  # paid, partial, pending, defaulted, etc.
    name = models.CharField(max_length=50)
    requires_reason = models.BooleanField(default=False)
    affects_outstanding = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Collection Status"
        verbose_name_plural = "Collection Statuses"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name


class ExpenseCategory(BaseModel):
    workspace = models.ForeignKey(
        "guest_workspace.GuestWorkspace",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="custom_expense_categories",
        help_text="Null for system default categories. Set for workspace-custom categories.",
    )
    code = models.CharField(max_length=50, db_index=True)  # fuel, food, travel, office, etc.
    name = models.CharField(max_length=100)
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} {'(System)' if self.is_system else ''}"


class BusinessCategory(BaseModel):
    code = models.CharField(max_length=50, unique=True, db_index=True)  # money_lending, pawn_broking, etc.
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Business Category"
        verbose_name_plural = "Business Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CustomerReview(BasePublicModel):
    author_name = models.CharField(max_length=120, db_index=True)
    business_name = models.CharField(max_length=150, blank=True)
    role_title = models.CharField(max_length=100, default="Lender")
    rating = models.PositiveIntegerField(default=5)
    review_text = models.TextField()
    avatar_url = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
        db_index=True,
    )
    is_approved = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name} ({self.rating}★) — {self.status}"
