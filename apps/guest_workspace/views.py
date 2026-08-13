"""
guest_workspace/views.py

API Views for Guest Workspace:
- Dashboard API
- Customer API (List, Create, Detail, Update, Delete)
- Collection API (List, Create, Batch, Detail, Update, Delete)
- Expense API (List, Create, Detail, Update, Delete)
- Reports API
- Calculator API
- Upgrade API
"""

import logging
from datetime import datetime, date as dt_date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema

from apps.common.permissions import IsGuestUser
from apps.common.responses import success_response, created_response, error_response
from apps.guest_workspace.serializers import (
    GuestWorkspaceSerializer,
    GuestWorkspaceUpdateSerializer,
    CustomerProfileListSerializer,
    CustomerProfileDetailSerializer,
    CustomerCreateUpdateSerializer,
    CollectionListSerializer,
    CollectionCreateSerializer,
    BatchCollectionSerializer,
    ExpenseListSerializer,
    ExpenseCreateSerializer,
    CalculatorRequestSerializer,
    CapitalEntrySerializer,
    CapitalEntryCreateSerializer,
    CollectionLineSerializer,
)
from apps.guest_workspace.services import (
    GuestWorkspaceService,
    CustomerService,
    CollectionService,
    ExpenseService,
    DashboardService,
    ReportService,
    CalculatorService,
    CapitalService,
)

logger = logging.getLogger(__name__)


# ─── Workspace Settings / Me ──────────────────────────────────────────────────

class WorkspaceDetailView(APIView):
    """
    GET  /api/v1/app/workspace/ — Get current workspace details.
    PATCH /api/v1/app/workspace/ — Update workspace details.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = GuestWorkspaceSerializer

    @extend_schema(responses={200: GuestWorkspaceSerializer})
    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = GuestWorkspaceSerializer(workspace)
        return success_response(data=serializer.data)

    @extend_schema(request=GuestWorkspaceUpdateSerializer, responses={200: GuestWorkspaceSerializer})
    def patch(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = GuestWorkspaceUpdateSerializer(workspace, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        updated = GuestWorkspaceService.update_workspace(workspace, serializer.validated_data)
        return success_response(
            data=GuestWorkspaceSerializer(updated).data,
            message="Workspace settings updated.",
        )


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/v1/app/dashboard/
    Main dashboard metrics and summary for `app.index.tsx`.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        stats = DashboardService.get_dashboard_stats(workspace)
        recent = DashboardService.get_recent_collections(workspace, limit=5)
        recent_serialized = CollectionListSerializer(recent, many=True).data

        return success_response(data={
            "metrics": stats,
            "recent_collections": recent_serialized,
        })


class WeeklySummaryView(APIView):
    """
    GET /api/v1/app/dashboard/weekly-summary/
    Weekly day-by-day collection breakdown.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        summary = DashboardService.get_weekly_summary(workspace)
        return success_response(data=summary)


# ─── Customers ────────────────────────────────────────────────────────────────

class CustomerListCreateView(APIView):
    """
    GET  /api/v1/app/customers/ — List workspace customers.
    POST /api/v1/app/customers/ — Create a new customer.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CustomerProfileListSerializer

    @extend_schema(responses={200: CustomerProfileListSerializer(many=True)})
    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        filters = {
            "status": request.query_params.get("status"),
            "search": request.query_params.get("search"),
            "collection_frequency": request.query_params.get("frequency"),
            "collection_day": request.query_params.get("collection_day"),
            "line": request.query_params.get("line"),
            "portion": request.query_params.get("portion"),
        }
        queryset = CustomerService.get_customer_list(workspace, filters)

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CustomerProfileListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=CustomerCreateUpdateSerializer, responses={201: CustomerProfileDetailSerializer})
    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = CustomerCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        customer = CustomerService.create_customer(
            workspace=workspace,
            validated_data=serializer.validated_data,
            created_by=request.user,
        )
        return created_response(
            data=CustomerProfileDetailSerializer(customer).data,
            message="Customer added successfully.",
        )


class CustomerDetailView(APIView):
    """
    GET    /api/v1/app/customers/{id}/ — Customer detail.
    PATCH  /api/v1/app/customers/{id}/ — Edit customer.
    DELETE /api/v1/app/customers/{id}/ — Archive customer.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CustomerProfileDetailSerializer

    @extend_schema(responses={200: CustomerProfileDetailSerializer})
    def get(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        customer = CustomerService.get_customer_detail(workspace, public_id)
        return success_response(data=CustomerProfileDetailSerializer(customer).data)

    @extend_schema(request=CustomerCreateUpdateSerializer, responses={200: CustomerProfileDetailSerializer})
    def patch(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = CustomerCreateUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        customer = CustomerService.update_customer(workspace, public_id, serializer.validated_data)
        return success_response(
            data=CustomerProfileDetailSerializer(customer).data,
            message="Customer updated.",
        )

    def delete(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        CustomerService.delete_customer(workspace, public_id)
        return success_response(message="Customer deleted successfully.")


class CustomerCollectionsView(APIView):
    """
    GET /api/v1/app/customers/{id}/collections/
    Get collection history for a specific customer.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CollectionListSerializer

    @extend_schema(responses={200: CollectionListSerializer(many=True)})
    def get(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        customer = CustomerService.get_customer_detail(workspace, public_id)
        collections = customer.collections.select_related("status", "payment_mode").order_by("-collection_date")
        
        serializer = CollectionListSerializer(collections, many=True)
        return success_response(data=serializer.data)


# ─── Collections ──────────────────────────────────────────────────────────────

class CollectionListCreateView(APIView):
    """
    GET  /api/v1/app/collections/ — List collections.
    POST /api/v1/app/collections/ — Record a single collection.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CollectionListSerializer

    @extend_schema(responses={200: CollectionListSerializer(many=True)})
    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        filters = {
            "date_from": request.query_params.get("date_from"),
            "date_to": request.query_params.get("date_to"),
            "customer": request.query_params.get("customer"),
            "status": request.query_params.get("status"),
            "payment_mode": request.query_params.get("payment_mode"),
            "line": request.query_params.get("line"),
            "portion": request.query_params.get("portion"),
        }
        queryset = CollectionService.get_collections(workspace, filters)

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CollectionListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=CollectionCreateSerializer, responses={201: CollectionListSerializer})
    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = CollectionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        collection = CollectionService.record_collection(
            workspace=workspace,
            validated_data=dict(serializer.validated_data),
            collected_by=request.user,
        )
        return created_response(
            data=CollectionListSerializer(collection).data,
            message="Collection recorded successfully.",
        )


class CollectionBatchView(APIView):
    """
    POST /api/v1/app/collections/batch/
    Record multiple collections atomically for a given date (`app.collections.batch.tsx`).
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = BatchCollectionSerializer

    @extend_schema(request=BatchCollectionSerializer, responses={201: CollectionListSerializer(many=True)})
    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = BatchCollectionSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        created_entries = CollectionService.record_batch_collections(
            workspace=workspace,
            collection_date=serializer.validated_data["collection_date"],
            entries=serializer.validated_data["entries"],
            collected_by=request.user,
        )

        return created_response(
            data=CollectionListSerializer(created_entries, many=True).data,
            message=f"Successfully recorded {len(created_entries)} collections.",
        )


class CollectionDetailView(APIView):
    """
    GET    /api/v1/app/collections/{id}/
    PATCH  /api/v1/app/collections/{id}/
    DELETE /api/v1/app/collections/{id}/
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CollectionListSerializer

    @extend_schema(responses={200: CollectionListSerializer})
    def get(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        collection = CollectionService.get_collection_detail(workspace, public_id)
        return success_response(data=CollectionListSerializer(collection).data)

    @extend_schema(request=CollectionCreateSerializer, responses={200: CollectionListSerializer})
    def patch(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = CollectionCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        collection = CollectionService.update_collection(
            workspace, public_id, serializer.validated_data, updated_by=request.user
        )
        return success_response(
            data=CollectionListSerializer(collection).data,
            message="Collection updated.",
        )

    def delete(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        CollectionService.delete_collection(workspace, public_id)
        return success_response(message="Collection deleted.")


# ─── Expenses ─────────────────────────────────────────────────────────────────

class ExpenseListCreateView(APIView):
    """
    GET  /api/v1/app/expenses/ — List expenses.
    POST /api/v1/app/expenses/ — Record expense.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = ExpenseListSerializer

    @extend_schema(responses={200: ExpenseListSerializer(many=True)})
    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        filters = {
            "date_from": request.query_params.get("date_from"),
            "date_to": request.query_params.get("date_to"),
            "category": request.query_params.get("category"),
            "payment_mode": request.query_params.get("payment_mode"),
        }
        queryset = ExpenseService.get_expenses(workspace, filters)

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ExpenseListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=ExpenseCreateSerializer, responses={201: ExpenseListSerializer})
    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = ExpenseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        expense = ExpenseService.create_expense(
            workspace=workspace,
            validated_data=dict(serializer.validated_data),
            created_by=request.user,
        )
        return created_response(
            data=ExpenseListSerializer(expense).data,
            message="Expense recorded successfully.",
        )


class ExpenseDetailView(APIView):
    """
    PATCH  /api/v1/app/expenses/{id}/
    DELETE /api/v1/app/expenses/{id}/
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = ExpenseListSerializer

    @extend_schema(request=ExpenseCreateSerializer, responses={200: ExpenseListSerializer})
    def patch(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = ExpenseCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        expense = ExpenseService.update_expense(workspace, public_id, dict(serializer.validated_data))
        return success_response(data=ExpenseListSerializer(expense).data, message="Expense updated.")

    def delete(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        ExpenseService.delete_expense(workspace, public_id)
        return success_response(message="Expense deleted.")


# ─── Reports & Export ─────────────────────────────────────────────────────────

class ReportsCollectionsView(APIView):
    """GET /api/v1/app/reports/collections/"""
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        report = ReportService.generate_collection_report(workspace, request.query_params)
        report["entries"] = CollectionListSerializer(report["entries"], many=True).data
        return success_response(data=report)


class ReportsCustomersView(APIView):
    """GET /api/v1/app/reports/customers/"""
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        report = ReportService.generate_customer_report(workspace, request.query_params)
        report["customers"] = CustomerProfileListSerializer(report["customers"], many=True).data
        return success_response(data=report)


class ReportsExpensesView(APIView):
    """GET /api/v1/app/reports/expenses/"""
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        report = ReportService.generate_expense_report(workspace, request.query_params)
        report["expenses"] = ExpenseListSerializer(report["expenses"], many=True).data
        return success_response(data=report)


class ReportsExportView(APIView):
    """GET /api/v1/app/reports/export/?type=collection&format=csv"""
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        report_type = request.query_params.get("type", "collection")
        fmt = request.query_params.get("format", "csv")

        if fmt == "csv":
            csv_content = ReportService.export_report_csv(workspace, report_type, request.query_params)
            response = HttpResponse(csv_content, content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{report_type}_report.csv"'
            return response
        else:
            return error_response("Format not supported yet.", http_status=400)


# ─── Calculator ───────────────────────────────────────────────────────────────

class CalculatorView(APIView):
    """
    POST /api/v1/app/calculator/
    Stateless loan calculator for `app.calculator.tsx`.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CalculatorRequestSerializer

    @extend_schema(request=CalculatorRequestSerializer)
    def post(self, request):
        serializer = CalculatorRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        result = CalculatorService.calculate_loan(**serializer.validated_data)
        return success_response(data=result)


# ─── Upgrade Flow ─────────────────────────────────────────────────────────────

class UpgradeView(APIView):
    """
    GET  /api/v1/app/upgrade/plans/ — View plans.
    POST /api/v1/app/upgrade/ — Request plan upgrade.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        from apps.administration.models import SubscriptionPlanConfig
        workspace = GuestWorkspaceService.get_workspace(request.user)
        limits = GuestWorkspaceService.get_effective_limits(workspace)

        db_plans = list(SubscriptionPlanConfig.objects.filter(is_active=True).order_by("sort_order", "monthly_price"))
        
        guest_plans = []
        lender_plans = []

        if db_plans:
            for p in db_plans:
                item = {
                    "code": p.plan_code,
                    "target_user_type": p.target_user_type,
                    "name": p.name,
                    "price": float(p.monthly_price),
                    "additional_days": p.additional_days,
                    "max_collection_days": 1 + p.additional_days if p.target_user_type == "guest" else p.max_collection_days,
                    "max_customers": p.max_customers,
                    "tagline": p.tagline,
                    "features": p.features,
                    "is_popular": p.is_popular,
                }
                if p.target_user_type == "lender":
                    lender_plans.append(item)
                else:
                    guest_plans.append(item)

        if not guest_plans:
            guest_plans = [
                {
                    "code": "plus_1_day",
                    "target_user_type": "guest",
                    "name": "+1 Collection Day",
                    "price": 199,
                    "additional_days": 1,
                    "max_collection_days": 2,
                    "tagline": "Add 1 additional collection day (Total 2 days/week)",
                    "features": ["2 Collection Business Days per week", "Unlimited Active Borrowers", "Loan Calculator & Passbook", "Standard Reports Export"],
                    "is_popular": False,
                },
                {
                    "code": "plus_2_days",
                    "target_user_type": "guest",
                    "name": "+2 Collection Days",
                    "price": 349,
                    "additional_days": 2,
                    "max_collection_days": 3,
                    "tagline": "Add 2 additional collection days (Total 3 days/week)",
                    "features": ["3 Collection Business Days per week", "Unlimited Active Borrowers", "Loan Calculator & Passbook", "Priority Support & CSV Export"],
                    "is_popular": True,
                },
                {
                    "code": "plus_3_days",
                    "target_user_type": "guest",
                    "name": "+3 Collection Days",
                    "price": 499,
                    "additional_days": 3,
                    "max_collection_days": 4,
                    "tagline": "Add 3 additional collection days (Total 4 days/week)",
                    "features": ["4 Collection Business Days per week", "Unlimited Active Borrowers", "Multi-Route Day Filtering", "Priority Support"],
                    "is_popular": False,
                },
                {
                    "code": "full_week",
                    "target_user_type": "guest",
                    "name": "Full Week (7 Days)",
                    "price": 899,
                    "additional_days": 6,
                    "max_collection_days": 7,
                    "tagline": "Unlimited collection business days (All 7 days/week)",
                    "features": ["7 Collection Business Days per week", "Unlimited Borrowers & Loans", "Complete Net Cash Flow Suite", "Dedicated Support Manager"],
                    "is_popular": False,
                },
            ]

        if not lender_plans:
            lender_plans = [
                {
                    "code": "lender_starter",
                    "target_user_type": "lender",
                    "name": "Lender ERP Starter",
                    "price": 1499,
                    "additional_days": 6,
                    "max_collection_days": 7,
                    "max_customers": 500,
                    "tagline": "Full finance company setup for small NBFCs & lending teams",
                    "features": [
                        "5 Field Agent / Staff Logins",
                        "Multi-Branch Architecture",
                        "GPS Staff Location Tracking",
                        "CIBIL & Bureau Score Check",
                        "Automated Overdue Recovery Flow",
                    ],
                    "is_popular": False,
                },
                {
                    "code": "lender_pro",
                    "target_user_type": "lender",
                    "name": "Lender ERP Institutional",
                    "price": 3999,
                    "additional_days": 6,
                    "max_collection_days": 7,
                    "max_customers": 2500,
                    "tagline": "Complete enterprise suite for scaling lending institutions",
                    "features": [
                        "25 Field Agent & Branch Manager Accounts",
                        "Real-time Field Staff Attendance & Route Tracking",
                        "Automated WhatsApp & SMS Payment Reminders",
                        "Loan Origination & Credit Underwriting",
                        "Advanced NPA Recovery & Legal Notices",
                        "24/7 Priority SLA & Account Manager",
                    ],
                    "is_popular": True,
                },
            ]

        return success_response(data={
            "current_plan": workspace.subscription_plan,
            "base_free_days": 1,
            "purchased_additional_days": workspace.purchased_additional_days,
            "total_allowed_days": workspace.max_allowed_collection_days,
            "current_limits": limits,
            "guest_plans": guest_plans,
            "lender_plans": lender_plans,
            "available_plans": guest_plans + lender_plans,
        })

    def post(self, request):
        from apps.administration.models import SubscriptionPlanConfig
        workspace = GuestWorkspaceService.get_workspace(request.user)
        plan_code = request.data.get("plan_code")
        additional_days = request.data.get("additional_days")

        if plan_code:
            config = SubscriptionPlanConfig.objects.filter(plan_code=plan_code).first()
            if config:
                additional_days = config.additional_days

        if additional_days is None:
            return error_response("Please specify plan_code or additional_days.", http_status=400)

        add_days = int(additional_days)
        workspace.purchased_additional_days = add_days
        if add_days > 0:
            workspace.subscription_plan = "premium"
        else:
            workspace.subscription_plan = "free"
            workspace.purchased_additional_days = 0
            workspace.max_collection_days_override = None
            workspace.allowed_collection_days = ["monday"]
        workspace.save()

        updated_limits = GuestWorkspaceService.get_effective_limits(workspace)

        return success_response(
            data={
                "current_plan": workspace.subscription_plan,
                "base_free_days": 1,
                "purchased_additional_days": workspace.purchased_additional_days,
                "total_allowed_days": workspace.max_allowed_collection_days,
                "limits": updated_limits,
            },
            message=f"Plan updated successfully! Your total allowed collection days is now {workspace.max_allowed_collection_days} days."
        )


class SubmitUpgradeRequestView(APIView):
    """
    POST /api/v1/app/upgrade/request/
    Submits a pending plan upgrade request when a user selects a plan.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def post(self, request):
        from apps.administration.models import PlanUpgradeRequest, SubscriptionPlanConfig
        from apps.guest_workspace.serializers import PlanUpgradeRequestSerializer

        workspace = GuestWorkspaceService.get_workspace(request.user)
        plan_code = request.data.get("plan_code")
        plan_name = request.data.get("plan_name", "Plan Upgrade")
        additional_days = request.data.get("additional_days", 1)
        amount = request.data.get("amount", 0)

        if plan_code:
            config = SubscriptionPlanConfig.objects.filter(plan_code=plan_code).first()
            if config:
                plan_name = config.name
                additional_days = config.additional_days
                amount = config.monthly_price

        req_obj = PlanUpgradeRequest.objects.create(
            workspace=workspace,
            requested_by=request.user,
            plan_code=plan_code or "guest_custom",
            plan_name=plan_name,
            additional_days=int(additional_days),
            amount=amount,
            status="pending",
        )

        return created_response(
            data=PlanUpgradeRequestSerializer(req_obj).data,
            message="Upgrade request submitted successfully. Pending admin approval.",
        )


class WorkspaceDataBackupView(APIView):
    """
    GET /api/v1/app/backup/download/
    Generates and downloads a complete JSON data backup of all workspace records
    (Customers, Loans, Collections, Expenses, Business Details) for offline safety.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        import json
        from django.utils import timezone
        from apps.guest_workspace.models import CustomerProfile, CollectionEntry, Expense
        from apps.guest_workspace.serializers import CustomerProfileSerializer, CollectionEntrySerializer, ExpenseSerializer, GuestWorkspaceSerializer
        from apps.audit_logs.services import AuditLogService
        from apps.audit_logs.models import ActionType

        workspace = GuestWorkspaceService.get_workspace(request.user)

        customers = CustomerProfile.objects.filter(workspace=workspace)
        collections = CollectionEntry.objects.filter(workspace=workspace)
        expenses = Expense.objects.filter(workspace=workspace)

        backup_payload = {
            "version": "1.0",
            "backup_timestamp": timezone.now().isoformat(),
            "workspace": GuestWorkspaceSerializer(workspace).data,
            "customers_count": customers.count(),
            "customers": CustomerProfileSerializer(customers, many=True).data,
            "collections_count": collections.count(),
            "collections": CollectionEntrySerializer(collections, many=True).data,
            "expenses_count": expenses.count(),
            "expenses": ExpenseSerializer(expenses, many=True).data,
        }

        AuditLogService.log_action(
            user=request.user,
            action=ActionType.EXPORT,
            target_model="GuestWorkspace",
            target_id=str(workspace.public_id),
            description=f"Downloaded complete workspace data backup ({customers.count()} borrowers, {collections.count()} collections)",
        )

        response = HttpResponse(json.dumps(backup_payload, indent=2), content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="finroute_backup_{workspace.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response


# ─── Capital Entries & Daily Cash Reconciliation ──────────────────────────────

class CapitalEntryView(APIView):
    """
    GET  /api/v1/app/capital/ — List starting route cash / capital entries.
    POST /api/v1/app/capital/ — Record a starting cash / capital entry.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    @extend_schema(responses={200: CapitalEntrySerializer(many=True)})
    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        entry_date_str = request.query_params.get("entry_date")
        entry_date = None
        if entry_date_str:
            from datetime import datetime
            try:
                entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        entries = CapitalService.get_capital_entries(workspace, entry_date=entry_date)
        serializer = CapitalEntrySerializer(entries, many=True)
        return success_response(data=serializer.data)

    @extend_schema(request=CapitalEntryCreateSerializer, responses={201: CapitalEntrySerializer})
    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        serializer = CapitalEntryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        entry = CapitalService.record_capital(
            workspace=workspace,
            entry_date=serializer.validated_data["entry_date"],
            amount=serializer.validated_data["amount"],
            remarks=serializer.validated_data.get("remarks", ""),
            added_by=request.user,
        )
        return created_response(
            data=CapitalEntrySerializer(entry).data,
            message="Starting cash / capital entry recorded successfully.",
        )


class CapitalEntryDetailView(APIView):
    """
    DELETE /api/v1/app/capital/{public_id}/ — Delete a capital entry.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def delete(self, request, public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        CapitalService.delete_capital(workspace, str(public_id))
        return success_response(message="Capital entry deleted successfully.")


class DailyCashReconciliationView(APIView):
    """
    GET /api/v1/app/cash-reconciliation/?date=YYYY-MM-DD
    Returns comprehensive daily route cash reconciliation:
    (Collections + Capital Injected) - (New Disbursements + Expenses)
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        from datetime import date as dt_date, datetime
        from django.db.models import Sum, Count
        from apps.guest_workspace.models import CustomerProfile, CollectionEntry, Expense, CapitalEntry

        workspace = GuestWorkspaceService.get_workspace(request.user)
        date_str = request.query_params.get("date")
        line_param = request.query_params.get("line")
        target_date = dt_date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        # 1. Collections Inflow
        collections_qs = CollectionEntry.objects.filter(
            workspace=workspace,
            collection_date=target_date,
        )
        if line_param and line_param != "all":
            collections_qs = collections_qs.filter(customer__line__public_id=line_param)

        collections_agg = collections_qs.aggregate(
            total=Sum("collected_amount"),
            count=Count("id"),
        )

        # 2. Capital Injections Inflow
        capital_agg = CapitalEntry.objects.filter(
            workspace=workspace,
            entry_date=target_date,
        ).aggregate(
            total=Sum("amount"),
            count=Count("id"),
        )

        # 3. Disbursements Outflow
        disbursements_qs = CustomerProfile.objects.filter(
            workspace=workspace,
            start_date=target_date,
        )
        if line_param and line_param != "all":
            disbursements_qs = disbursements_qs.filter(line__public_id=line_param)

        disbursements_agg = disbursements_qs.aggregate(
            total=Sum("disbursed_amount"),
            count=Count("id"),
        )

        # 4. Expenses Outflow
        expenses_agg = Expense.objects.filter(
            workspace=workspace,
            expense_date=target_date,
        ).aggregate(
            total=Sum("amount"),
            count=Count("id"),
        )

        collections_total = float(collections_agg["total"] or 0)
        capital_total = float(capital_agg["total"] or 0)
        disbursements_total = float(disbursements_agg["total"] or 0)
        expenses_total = float(expenses_agg["total"] or 0)

        total_inflow = collections_total + capital_total
        total_outflow = disbursements_total + expenses_total
        net_cash_handheld = total_inflow - total_outflow

        return success_response(data={
            "date": target_date.isoformat(),
            "collections_total": collections_total,
            "collections_count": collections_agg["count"] or 0,
            "capital_total": capital_total,
            "capital_count": capital_agg["count"] or 0,
            "disbursements_total": disbursements_total,
            "disbursements_count": disbursements_agg["count"] or 0,
            "expenses_total": expenses_total,
            "expenses_count": expenses_agg["count"] or 0,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_cash_handheld": net_cash_handheld,
            "is_cash_deficit": net_cash_handheld < 0,
        })


class TriggerDailyRouteEmailsView(APIView):
    """
    POST /api/v1/app/reports/trigger-daily-emails/
    Triggers the evening collection email dispatch with Excel attachments for active route lines.
    Secured via optional X-Cron-Secret header or logged-in user authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            from django.conf import settings
            import os
            expected_secret = getattr(settings, 'CRON_SECRET_KEY', 'finroute_cron_secret_2026') or os.environ.get('CRON_SECRET_KEY', 'finroute_cron_secret_2026')
            provided_secret = request.headers.get("X-Cron-Secret") or request.query_params.get("secret")

            is_authenticated_user = request.user and request.user.is_authenticated
            if not is_authenticated_user and provided_secret != expected_secret:
                return error_response(message="Authentication required or invalid X-Cron-Secret key.", http_status=status.HTTP_403_FORBIDDEN)

            date_str = None
            try:
                if hasattr(request, "data") and isinstance(request.data, dict):
                    date_str = request.data.get("date")
            except Exception:
                pass
            if not date_str and hasattr(request, "query_params"):
                date_str = request.query_params.get("date")

            target_date = dt_date.today()
            if date_str:
                try:
                    target_date = datetime.strptime(str(date_str), "%Y-%m-%d").date()
                except ValueError:
                    pass

            today_weekday = target_date.strftime("%A").lower()
            from apps.guest_workspace.services.route_email_report_service import RouteEmailReportService
            from apps.guest_workspace.models import GuestWorkspace, CollectionLine

            workspaces_qs = GuestWorkspace.objects.filter(status="active")

            # If user is authenticated, limit to their workspace only
            if request.user and request.user.is_authenticated:
                try:
                    ws = GuestWorkspaceService.get_workspace(request.user)
                    workspaces_qs = GuestWorkspace.objects.filter(id=ws.id)
                except Exception:
                    pass

            sent_results = []
            for ws in workspaces_qs:
                lines = CollectionLine.objects.filter(workspace=ws, is_active=True).prefetch_related("day_schedules")
                matching_lines = []
                for line in lines:
                    if line.day_schedules.filter(day_of_week__iexact=today_weekday).exists():
                        matching_lines.append(line)

                if not matching_lines:
                    matching_lines = list(lines) if lines.exists() else [None]

                for line in matching_lines:
                    sent = False
                    error_msg = None
                    try:
                        sent = RouteEmailReportService.send_route_email(
                            workspace=ws,
                            line=line,
                            target_date=target_date,
                        )
                    except Exception as ex:
                        logger.error("Error triggering route email for line %s in workspace %s: %s", line, ws.name, ex, exc_info=True)
                        error_msg = str(ex)

                    sent_results.append({
                        "workspace": ws.name,
                        "line": line.name if line else "All Lines",
                        "sent": sent,
                        "error": error_msg,
                    })

            return success_response(data={
                "date": target_date.isoformat(),
                "results": sent_results,
                "message": f"Daily evening route emails triggered for {len(sent_results)} route lines across {workspaces_qs.count()} workspace(s).",
            })
        except Exception as top_err:
            logger.error("Unhandled error in TriggerDailyRouteEmailsView: %s", top_err, exc_info=True)
            return error_response(message=f"Failed to trigger route emails: {str(top_err)}", http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendRouteClosureReportView(APIView):
    """
    POST /api/v1/app/cash-reconciliation/send-report/
    Generates and emails a full daily route reconciliation report to the workspace owner.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        # Extract guest user email address
        guest_user = request.user
        target_email = getattr(guest_user, "email", None)
        if not target_email and hasattr(workspace, "owner") and workspace.owner:
            target_email = getattr(workspace.owner, "email", None)
        if not target_email and hasattr(guest_user, "username") and "@" in str(guest_user.username):
            target_email = guest_user.username

        if not target_email:
            target_email = "owner@fin-route.site"

        date_str = None
        line_param = None
        line_name = "Selected Route Line"
        try:
            if hasattr(request, "data") and isinstance(request.data, dict):
                date_str = request.data.get("date")
                line_param = request.data.get("line")
                line_name = request.data.get("line_name", "Selected Route Line")
        except Exception:
            pass

        target_date = dt_date.today()
        if date_str:
            try:
                target_date = datetime.strptime(str(date_str), "%Y-%m-%d").date()
            except ValueError:
                pass

        # 1. Paid Collection Entries
        collections_qs = CollectionEntry.objects.filter(workspace=workspace, collection_date=target_date).select_related("customer")
        if line_param and line_param != "all":
            collections_qs = collections_qs.filter(customer__line__public_id=line_param)

        paid_entries = collections_qs.filter(collected_amount__gt=0).exclude(status_code="skipped")
        skipped_entries = collections_qs.filter(status_code="skipped")

        # 2. Query line customers for unpaid borrower breakdown
        line_customers_qs = CustomerProfile.objects.filter(workspace=workspace).select_related("line")
        if line_param and line_param != "all":
            line_customers_qs = line_customers_qs.filter(line__public_id=line_param)

        paid_customer_ids = set(paid_entries.values_list("customer_id", flat=True))
        logged_skipped_ids = set(skipped_entries.values_list("customer_id", flat=True))
        unpaid_customers = line_customers_qs.exclude(id__in=paid_customer_ids | logged_skipped_ids)

        # 3. Query Capital
        capital_agg = CapitalEntry.objects.filter(workspace=workspace, entry_date=target_date).aggregate(total=Sum("amount"), count=Count("id"))

        # 4. Query Disbursements
        disbursements_qs = CustomerProfile.objects.filter(workspace=workspace, start_date=target_date)
        if line_param and line_param != "all":
            disbursements_qs = disbursements_qs.filter(line__public_id=line_param)
        disbursements_agg = disbursements_qs.aggregate(total=Sum("disbursed_amount"), count=Count("id"))

        # 5. Query Expenses
        expenses_agg = Expense.objects.filter(workspace=workspace, expense_date=target_date).aggregate(total=Sum("amount"), count=Count("id"))

        col_tot = float(paid_entries.aggregate(total=Sum("collected_amount"))["total"] or 0)
        cap_tot = float(capital_agg["total"] or 0)
        disb_tot = float(disbursements_agg["total"] or 0)
        exp_tot = float(expenses_agg["total"] or 0)
        net_cash = (col_tot + cap_tot) - (disb_tot + exp_tot)

        # Build Paid Customers HTML Rows
        paid_rows_html = ""
        for p in paid_entries:
            c = p.customer
            c_name = c.full_name if c else (p.customer_name or "N/A")
            c_code = c.customer_code if c else (p.customer_code or "")
            paid_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{c_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({c_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 800; color: #059669; text-align: right;">+₹{float(p.collected_amount):,.2f}</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #ecfdf5; color: #047857; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Paid</span></td>
            </tr>
            """
        if not paid_rows_html:
            paid_rows_html = """<tr><td colspan="3" style="padding: 12px; text-align: center; color: #94a3b8; font-size: 12px;">No payment receipts recorded for this route today.</td></tr>"""

        # Build Skipped & Unpaid Customers HTML Rows
        skipped_rows_html = ""
        for s in skipped_entries:
            c = s.customer
            c_name = c.full_name if c else (s.customer_name or "N/A")
            c_code = c.customer_code if c else (s.customer_code or "")
            skipped_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{c_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({c_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 700; color: #e11d48; text-align: right;">Skipped</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #fff1f2; color: #e11d48; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Skipped</span></td>
            </tr>
            """
        for u in unpaid_customers:
            skipped_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{u.full_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({u.customer_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 700; color: #d97706; text-align: right;">₹{float(u.installment_amount or u.loan_amount or 0):,.2f}</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #fef3c7; color: #b45309; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">Unpaid</span></td>
            </tr>
            """
        if not skipped_rows_html:
            skipped_rows_html = """<tr><td colspan="3" style="padding: 12px; text-align: center; color: #059669; font-size: 12px;">🎉 100% Collection Completed! All borrowers paid today.</td></tr>"""

        # Build New Disbursements HTML Rows
        disbursed_rows_html = ""
        for d in disbursements_qs:
            disbursed_rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
              <td style="padding: 10px 12px; font-weight: 700; color: #1e293b;">{d.full_name} <span style="font-size: 11px; font-weight: normal; color: #64748b;">({d.customer_code})</span></td>
              <td style="padding: 10px 12px; font-family: monospace; font-weight: 800; color: #7c3aed; text-align: right;">−₹{float(d.disbursed_amount):,.2f}</td>
              <td style="padding: 10px 12px; text-align: center;"><span style="background: #f3e8ff; color: #6b21a8; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">New Loan</span></td>
            </tr>
            """

        subject = f"FinRoute Daily Closure Report: {line_name} ({target_date.strftime('%d %b %Y')})"

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; color: #1e293b; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); padding: 28px 24px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }}
            .header p {{ margin: 6px 0 0 0; opacity: 0.9; font-size: 13px; }}
            .body {{ padding: 24px; }}
            .badge {{ display: inline-block; background: #ecfdf5; color: #047857; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid #a7f3d0; margin-bottom: 20px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; text-align: left; }}
            .card-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 4px; }}
            .card-val {{ font-size: 20px; font-weight: 800; font-family: monospace; margin: 0; }}
            .green {{ color: #059669; }}
            .blue {{ color: #2563eb; }}
            .purple {{ color: #7c3aed; }}
            .rose {{ color: #e11d48; }}
            .section-header {{ font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #334155; margin: 24px 0 10px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }}
            .table-container {{ width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; margin-bottom: 16px; font-size: 13px; }}
            .table-container th {{ background: #f1f5f9; padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #475569; }}
            .summary-box {{ background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 14px; padding: 20px; margin-top: 20px; }}
            .summary-title {{ font-size: 12px; font-weight: 800; text-transform: uppercase; color: #065f46; }}
            .summary-val {{ font-size: 26px; font-weight: 900; color: #047857; font-family: monospace; margin-top: 4px; }}
            .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📊 FinRoute Daily Route Closure Report</h1>
              <p>{workspace.name} • {line_name}</p>
            </div>
            <div class="body">
              <div style="text-align: center;">
                <span class="badge">📅 Route Date: {target_date.strftime('%d %B %Y')}</span>
              </div>

              <!-- 4-PILLAR RECONCILIATION CARDS -->
              <table width="100%" style="border-collapse: separate; border-spacing: 8px;">
                <tr>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">📥 Collections ({paid_entries.count()} Paid)</div>
                      <div class="card-val green">₹{col_tot:,.2f}</div>
                    </div>
                  </td>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">💵 Starting Cash ({capital_agg['count'] or 0} Injected)</div>
                      <div class="card-val blue">₹{cap_tot:,.2f}</div>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">📤 Disbursed ({disbursements_agg['count'] or 0} New Loans)</div>
                      <div class="card-val purple">₹{disb_tot:,.2f}</div>
                    </div>
                  </td>
                  <td width="50%">
                    <div class="card">
                      <div class="card-title">💸 Expenses ({expenses_agg['count'] or 0} Entries)</div>
                      <div class="card-val rose">₹{exp_tot:,.2f}</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- NET CASH SUMMARY BOX -->
              <div class="summary-box">
                <div class="summary-title">💰 Final Closing Handheld Cash</div>
                <div style="font-size: 11px; color: #047857; margin-top: 2px;">(Starting Cash + Collections) − (Disbursements + Expenses)</div>
                <div class="summary-val">₹{net_cash:,.2f}</div>
              </div>

              <!-- 1. PAID BORROWERS LIST -->
              <div class="section-header" style="color: #059669;">📥 Paid Customers ({paid_entries.count()})</div>
              <table class="table-container">
                <thead>
                  <tr>
                    <th>Borrower Name & Code</th>
                    <th style="text-align: right;">Amount Paid</th>
                    <th style="text-align: center;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paid_rows_html}
                </tbody>
              </table>

              <!-- 2. SKIPPED & UNPAID BORROWERS LIST -->
              <div class="section-header" style="color: #e11d48;">🔴 Skipped / Unpaid Customers ({skipped_entries.count() + unpaid_customers.count()})</div>
              <table class="table-container">
                <thead>
                  <tr>
                    <th>Borrower Name & Code</th>
                    <th style="text-align: right;">Installment Due</th>
                    <th style="text-align: center;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {skipped_rows_html}
                </tbody>
              </table>

              <!-- 3. NEW BORROWER DISBURSEMENTS (IF ANY) -->
              {f'''
              <div class="section-header" style="color: #7c3aed;">📤 New Loan Disbursements ({disbursements_qs.count()})</div>
              <table class="table-container">
                <thead>
                  <tr>
                    <th>Borrower Name & Code</th>
                    <th style="text-align: right;">Loan Disbursed</th>
                    <th style="text-align: center;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {disbursed_rows_html}
                </tbody>
              </table>
              ''' if disbursed_rows_html else ''}

            </div>
            <div class="footer">
              Automated Route Reconciliation Report generated by <b>FinRoute Platform</b>.<br/>
              © 2026 FinRoute Finance Systems.
            </div>
          </div>
        </body>
        </html>
        """

        from django.conf import settings
        from django.core.mail import send_mail

        email_sent = False
        resend_key = getattr(settings, 'RESEND_API_KEY', '') or os.environ.get('RESEND_API_KEY', '')
        if resend_key:
            try:
                import resend
                resend.api_key = resend_key
                resend.Emails.send({
                    "from": "FinRoute Reports <info@fin-route.site>",
                    "to": [target_email],
                    "subject": subject,
                    "html": html_message,
                })
                email_sent = True
                logger.info("Sent route closure email via Resend API to %s", target_email)
            except Exception as r_err:
                logger.warning("Resend email error: %s. Trying django send_mail...", r_err)

        if not email_sent:
            try:
                send_mail(
                    subject=subject,
                    message=f"Daily Route Closure Report for {line_name} on {target_date}.\nFinal Cash in Hand: ₹{net_cash:,.2f}",
                    html_message=html_message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'FinRoute <info@fin-route.site>'),
                    recipient_list=[target_email],
                    fail_silently=False,
                )
                email_sent = True
                logger.info("Sent route closure email via Django send_mail to %s", target_email)
            except Exception as e_err:
                logger.error("Failed to send route closure email: %s", e_err)

        return success_response(data={
            "email_sent": email_sent,
            "recipient": target_email,
            "message": f"Daily route closure report emailed to {target_email}",
        })


# ─── Collection Line Views ───────────────────────────────────────────────────

class LineListCreateView(APIView):
    """
    GET /api/v1/app/lines/ — List active collection lines
    POST /api/v1/app/lines/ — Create a new collection line with weekday portions
    """
    permission_classes = [IsAuthenticated, IsGuestUser]
    serializer_class = CollectionLineSerializer

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        from apps.guest_workspace.services.line_service import LineService
        lines = LineService.get_lines(workspace)
        serializer = CollectionLineSerializer(lines, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        from apps.guest_workspace.serializers import LineCreateSerializer
        serializer = LineCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        from apps.guest_workspace.services.line_service import LineService
        line = LineService.create_line(
            workspace=workspace,
            name=serializer.validated_data["name"],
            area=serializer.validated_data.get("area", ""),
            schedules=serializer.validated_data.get("schedules", []),
            created_by=request.user,
        )
        return created_response(
            data=CollectionLineSerializer(line).data,
            message="Collection line created successfully.",
        )


class LineDetailView(APIView):
    """
    GET /api/v1/app/lines/<uuid:line_public_id>/
    PATCH /api/v1/app/lines/<uuid:line_public_id>/
    DELETE /api/v1/app/lines/<uuid:line_public_id>/
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request, line_public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        from apps.guest_workspace.services.line_service import LineService
        line = LineService.get_line_detail(workspace, str(line_public_id))
        return success_response(data=CollectionLineSerializer(line).data)

    def patch(self, request, line_public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        from apps.guest_workspace.services.line_service import LineService
        line = LineService.update_line(
            workspace=workspace,
            line_public_id=str(line_public_id),
            name=request.data.get("name"),
            area=request.data.get("area"),
            schedules=request.data.get("schedules"),
        )
        return success_response(
            data=CollectionLineSerializer(line).data,
            message="Collection line updated successfully.",
        )

    def delete(self, request, line_public_id):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        from apps.guest_workspace.services.line_service import LineService
        LineService.delete_line(workspace, str(line_public_id))
        return success_response(message="Collection line deleted successfully.")


class AvailablePortionsView(APIView):
    """
    GET /api/v1/app/lines/available-portions/
    Returns available day portions (morning, afternoon, both) per day of week.
    """
    permission_classes = [IsAuthenticated, IsGuestUser]

    def get(self, request):
        workspace = GuestWorkspaceService.get_workspace(request.user)
        exclude_id = request.query_params.get("exclude_line_id")
        from apps.guest_workspace.services.line_service import LineService
        portions = LineService.get_available_day_portions(
            workspace=workspace,
            exclude_line_id=int(exclude_id) if exclude_id and str(exclude_id).isdigit() else None,
        )
        return success_response(data=portions)


