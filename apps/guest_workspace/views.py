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
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
)
from apps.guest_workspace.services import (
    GuestWorkspaceService,
    CustomerService,
    CollectionService,
    ExpenseService,
    DashboardService,
    ReportService,
    CalculatorService,
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
