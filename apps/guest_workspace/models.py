"""
guest_workspace/models.py

Models for the Guest Workspace — the core V1 product.

Workspace → Customers → Collections → Expenses

Design rules:
- All financial amounts use DecimalField(max_digits=12, decimal_places=2).
- outstanding_balance is maintained via service calls after every collection.
- Plan limits are enforced in the service layer, not at the model level.
- All workspace-scoped models include `workspace` as the first FK.
"""

from django.db import models
from apps.common.models import BaseModel, BasePublicModel


# ─── Plan and Status Choices ─────────────────────────────────────────────────

class SubscriptionPlan(models.TextChoices):
    GUEST = "guest", "Guest Free"
    FREE = "free", "Free"
    STARTER = "starter", "ERP Starter"
    PREMIUM = "premium", "Premium"
    ENTERPRISE = "enterprise", "Enterprise"


class WorkspaceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    READ_ONLY = "read_only", "Read Only"


class CustomerStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CLOSED = "closed", "Closed"
    DEFAULTED = "defaulted", "Defaulted"
    SUSPENDED = "suspended", "Suspended"


class DayPortionChoices(models.TextChoices):
    MORNING = "morning", "Morning (1:00 AM – 1:00 PM)"
    AFTERNOON = "afternoon", "Afternoon / Evening (1:00 PM – 12:00 AM)"
    BOTH = "both", "Full Day (Both Portions)"


# ─── GuestWorkspace ───────────────────────────────────────────────────────────

class GuestWorkspace(BasePublicModel):
    """
    Represents a single-user money lending business workspace.
    Created automatically when a Guest user registers.

    One GuestWorkspace per User (OneToOne).
    All data (customers, collections, expenses) belongs to this workspace.
    """

    owner = models.OneToOneField(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="guest_workspace",
        help_text="The user who owns and manages this workspace.",
    )
    name = models.CharField(
        max_length=200,
        help_text="Business name, e.g. 'Ramesh Finance'.",
    )
    business_category = models.ForeignKey(
        "masters.BusinessCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workspaces",
        help_text="Type of finance business.",
    )
    mobile_number = models.CharField(
        max_length=15,
        help_text="Business contact number.",
    )
    logo = models.ImageField(
        upload_to="workspace_logos/",
        null=True,
        blank=True,
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)
    gstin = models.CharField(max_length=20, blank=True, null=True, default="")
    business_type = models.CharField(max_length=100, blank=True, null=True, default="")
    owner_pan = models.CharField(max_length=20, blank=True, null=True, default="")

    # --- Subscription ---
    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=WorkspaceStatus.choices,
        default=WorkspaceStatus.ACTIVE,
        db_index=True,
    )

    # --- Admin Overrides (set by Super Admin for special cases) ---
    max_customers_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="If set, overrides the plan's default customer limit for this workspace.",
    )
    max_collection_days_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="If set, overrides the plan's default weekly collection day limit.",
    )
    allowed_collection_days = models.JSONField(
        default=list,
        blank=True,
        help_text="Configured collection days of week for this workspace e.g. ['wednesday'].",
    )

    purchased_additional_days = models.PositiveIntegerField(
        default=0,
        help_text="Number of additional collection days purchased by the guest user.",
    )

    class Meta:
        verbose_name = "Guest Workspace"
        verbose_name_plural = "Guest Workspaces"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.owner.mobile_number}) [{self.subscription_plan}]"

    @property
    def is_active(self):
        return self.status == WorkspaceStatus.ACTIVE

    @property
    def is_suspended(self):
        return self.status == WorkspaceStatus.SUSPENDED

    @property
    def max_allowed_collection_days(self) -> int:
        if self.max_collection_days_override is not None:
            return self.max_collection_days_override
        base_days = 1  # Free tier base: 1 day per week
        total_days = base_days + self.purchased_additional_days
        return min(total_days, 7)


# ─── Collection Line (Route) & Schedule ───────────────────────────────────────

class CollectionLine(BasePublicModel):
    """
    Represents a geographic or route collection unit (Line / Business Route).
    E.g. 'Line 1 - Market Area', 'Kukatpally Route'.
    """

    workspace = models.ForeignKey(
        GuestWorkspace,
        on_delete=models.CASCADE,
        related_name="lines",
        db_index=True,
    )
    name = models.CharField(
        max_length=150,
        help_text="Name of the line/route e.g. Line 1 - Market Area.",
    )
    area = models.CharField(
        max_length=200,
        blank=True,
        help_text="Area or locality details e.g. Market Road, Sector 4.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="created_lines",
    )

    class Meta:
        verbose_name = "Collection Line"
        verbose_name_plural = "Collection Lines"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["workspace", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class LineDaySchedule(BasePublicModel):
    """
    Assigns a weekday and time portion (Morning 1am-1pm / Afternoon 1pm-12am / Both) to a Line.
    Capacity rule: A (day_of_week, portion) pair cannot conflict across lines in the same workspace.
    """

    line = models.ForeignKey(
        CollectionLine,
        on_delete=models.CASCADE,
        related_name="day_schedules",
        db_index=True,
    )
    day_of_week = models.CharField(
        max_length=20,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        db_index=True,
    )
    portion = models.CharField(
        max_length=20,
        choices=DayPortionChoices.choices,
        default=DayPortionChoices.BOTH,
        db_index=True,
    )

    class Meta:
        verbose_name = "Line Day Schedule"
        verbose_name_plural = "Line Day Schedules"
        ordering = ["day_of_week", "portion"]
        unique_together = ["line", "day_of_week"]

    def __str__(self):
        return f"{self.line.name} — {self.day_of_week} ({self.portion})"


# ─── Customer Profile ─────────────────────────────────────────────────────────

class CollectionDayChoices(models.TextChoices):
    MONDAY = "monday", "Monday"
    TUESDAY = "tuesday", "Tuesday"
    WEDNESDAY = "wednesday", "Wednesday"
    THURSDAY = "thursday", "Thursday"
    FRIDAY = "friday", "Friday"
    SATURDAY = "saturday", "Saturday"
    SUNDAY = "sunday", "Sunday"


class CustomerProfile(BasePublicModel):
    """
    Represents a borrower/customer in a Guest Workspace.

    Financial fields (loan_amount, interest_rate, etc.) define the terms.
    outstanding_balance is maintained in real-time by CollectionService.

    Auto-generated customer_code format: FR{workspace_id:03d}{sequence:04d}
    """

    workspace = models.ForeignKey(
        GuestWorkspace,
        on_delete=models.CASCADE,
        related_name="customers",
        db_index=True,
    )
    customer_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Auto-generated unique identifier, e.g. FR0010042.",
    )
    sequence_number = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Custom sequence or order number for borrower.",
    )

    # --- Personal Info ---
    full_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15)
    alternate_mobile = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to="customer_photos/", null=True, blank=True)
    id_proof_type = models.CharField(max_length=50, blank=True)
    id_proof_number = models.CharField(max_length=50, blank=True)

    # --- Address ---
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)

    # --- Loan Terms ---
    collection_frequency = models.ForeignKey(
        "masters.CollectionFrequency",
        on_delete=models.PROTECT,
        related_name="customers",
    )
    interest_type = models.ForeignKey(
        "masters.InterestType",
        on_delete=models.PROTECT,
        related_name="customers",
    )
    interest_rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        help_text="Interest rate as a decimal, e.g. 2.5 for 2.5%.",
    )
    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Original principal amount.",
    )
    disbursed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Actual amount handed to the customer.",
    )
    total_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total repayable amount (principal + interest). Auto-calculated on save.",
    )
    outstanding_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_index=True,
        help_text="Remaining amount to be collected. Updated by CollectionService.",
    )

    # --- Schedule & Installments ---
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_existing_borrower = models.BooleanField(
        default=False,
        help_text="Flag indicating if the customer was imported as an ongoing loan with prior payments.",
    )
    total_installments = models.PositiveIntegerField(
        default=1,
        help_text="Total number of planned collection installments for this loan.",
    )
    installments_paid_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of installments already collected before or during workspace creation.",
    )
    remaining_installments_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of installments remaining to be collected.",
    )
    amount_already_collected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Amount already collected prior to workspace creation.",
    )
    installment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Custom per-installment collection amount for this borrower.",
    )
    collection_day = models.CharField(
        max_length=20,
        choices=CollectionDayChoices.choices,
        default=CollectionDayChoices.MONDAY,
        db_index=True,
        help_text="Assigned day of the week for weekly/scheduled collections.",
    )
    line = models.ForeignKey(
        CollectionLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers",
        db_index=True,
        help_text="The collection route/line this customer belongs to.",
    )
    portion = models.CharField(
        max_length=20,
        choices=DayPortionChoices.choices,
        default=DayPortionChoices.BOTH,
        db_index=True,
        help_text="Assigned day portion (Morning 1am-1pm / Afternoon 1pm-12am / Both).",
    )

    # --- Status ---
    status = models.CharField(
        max_length=20,
        choices=CustomerStatus.choices,
        default=CustomerStatus.ACTIVE,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    # --- Audit ---
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="created_customers",
    )

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "customer_code"]),
            models.Index(fields=["workspace", "start_date"]),
            models.Index(fields=["mobile_number"]),
        ]

    def __str__(self):
        return f"{self.customer_code} — {self.full_name} ({self.workspace.name})"


# ─── Collection Entry ─────────────────────────────────────────────────────────

class CollectionEntry(BasePublicModel):
    """
    A single collection event — payment received from a customer.

    Key rules:
    - Plan limits are checked in CollectionService before saving.
    - outstanding_balance on CustomerProfile is updated after each save.
    - receipt_number is auto-generated in the service layer.
    - GPS coordinates are optional (used in V2 field app).
    """

    workspace = models.ForeignKey(
        GuestWorkspace,
        on_delete=models.CASCADE,
        related_name="collections",
        db_index=True,
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="collections",
        db_index=True,
    )
    collection_date = models.DateField(
        db_index=True,
        help_text="The date the collection was recorded for.",
    )

    # --- Amounts ---
    expected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="What was scheduled to be collected.",
    )
    collected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="What was actually collected.",
    )

    # --- Status & Payment ---
    status = models.ForeignKey(
        "masters.CollectionStatus",
        on_delete=models.PROTECT,
        related_name="collection_entries",
    )
    payment_mode = models.ForeignKey(
        "masters.PaymentMode",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="collection_entries",
    )
    remarks = models.TextField(blank=True)
    is_collected_today = models.BooleanField(
        default=True,
        db_index=True,
        help_text="True if collected today, False if past/backdated collection.",
    )
    is_edited = models.BooleanField(
        default=False,
        help_text="True if this collection entry record/date was edited once.",
    )
    edit_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this collection entry was edited (Max allowed: 1).",
    )

    # --- Receipt ---
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Auto-generated receipt number.",
    )

    # --- GPS (V2 field app) ---
    gps_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )
    gps_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
    )

    # --- Audit ---
    collected_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="collections",
    )

    class Meta:
        verbose_name = "Collection Entry"
        verbose_name_plural = "Collection Entries"
        ordering = ["-collection_date", "-created_at"]
        indexes = [
            models.Index(fields=["workspace", "collection_date"]),
            models.Index(fields=["customer", "collection_date"]),
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self):
        return f"Collection({self.receipt_number}, {self.customer.full_name}, {self.collection_date})"


# ─── Expense ──────────────────────────────────────────────────────────────────

class Expense(BasePublicModel):
    """
    An operational expense for the workspace.
    E.g. fuel, office supplies, food expenses.
    """

    workspace = models.ForeignKey(
        GuestWorkspace,
        on_delete=models.CASCADE,
        related_name="expenses",
        db_index=True,
    )
    category = models.ForeignKey(
        "masters.ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    payment_mode = models.ForeignKey(
        "masters.PaymentMode",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    receipt_image = models.ImageField(
        upload_to="expense_receipts/",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ["-expense_date", "-created_at"]
        indexes = [
            models.Index(fields=["workspace", "expense_date"]),
            models.Index(fields=["workspace", "category"]),
        ]

    def __str__(self):
        return f"Expense({self.workspace.name}, {self.category.name}, {self.amount})"


# ─── Capital Entries (Opening Cash / Inflows) ─────────────────────────────────

class CapitalEntry(BasePublicModel):
    """
    Represents starting route cash or capital injection added by the lender for a given date.
    Used for daily cash reconciliation: (Collections + Capital) - (Disbursements + Expenses).
    """

    workspace = models.ForeignKey(
        GuestWorkspace,
        on_delete=models.CASCADE,
        related_name="capital_entries",
        db_index=True,
    )
    entry_date = models.DateField(
        db_index=True,
        help_text="The date this starting cash/capital was injected for.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="The amount of capital/cash added.",
    )
    remarks = models.TextField(
        blank=True,
        help_text="Optional description e.g. Starting cash brought from home/bank.",
    )
    added_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="capital_entries",
    )

    class Meta:
        verbose_name = "Capital Entry"
        verbose_name_plural = "Capital Entries"
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["workspace", "entry_date"]),
        ]

    def __str__(self):
        return f"CapitalEntry({self.workspace.name}, {self.entry_date}, ₹{self.amount})"

