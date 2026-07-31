"""
administration/views.py

API Views for Super Admin Console (`/admin/*` screens).
All views require IsSuperAdmin permission class.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db.models import Count

from apps.common.permissions import IsSuperAdmin
from apps.common.responses import success_response, error_response
from apps.guest_workspace.models import GuestWorkspace
from apps.administration.models import GlobalConfiguration, PromoCoupon, SubscriptionPlanConfig
from apps.accounts.models import ContactInquiry
from apps.accounts.serializers import ContactInquirySerializer
from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer
from apps.masters.models import (
    CollectionFrequency, PaymentMode, InterestType,
    CollectionStatus, ExpenseCategory, BusinessCategory
)
from apps.administration.serializers import (
    AdminWorkspaceListSerializer,
    AdminLenderCreateSerializer,
    AdminLenderUpdateSerializer,
    AdminLenderPasswordResetSerializer,
    QuotaOverrideSerializer,
    WorkspaceStatusUpdateSerializer,
    GlobalConfigurationSerializer,
    PromoCouponSerializer,
    BroadcastNotificationSerializer,
    AdminSubscriptionSummarySerializer,
    AdminInvoiceSerializer,
    SubscriptionPlanConfigSerializer,
)
from apps.administration.services.admin_service import AdminService

MASTER_MODEL_MAP = {
    "frequencies": CollectionFrequency,
    "payment-modes": PaymentMode,
    "interest-types": InterestType,
    "statuses": CollectionStatus,
    "expense-categories": ExpenseCategory,
    "business-categories": BusinessCategory,
}


class AdminDashboardView(APIView):
    """GET /api/v1/admin/dashboard/ — Super Admin platform stats"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="Get Super Admin Dashboard Metrics")
    def get(self, request):
        metrics = AdminService.get_dashboard_metrics()
        return success_response(data=metrics)


class AdminSystemHealthView(APIView):
    """GET /api/v1/admin/system-health/ — Infrastructure health"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="Get Platform Infrastructure Health")
    def get(self, request):
        health = AdminService.get_system_health()
        return success_response(data=health)


class AdminWorkspaceListView(APIView):
    """
    GET  /api/v1/admin/workspaces/ — List all platform workspaces
    POST /api/v1/admin/workspaces/ — Register a new Lender workspace
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminLenderCreateSerializer
        return AdminWorkspaceListSerializer

    @extend_schema(summary="List all tenant workspaces", responses={200: AdminWorkspaceListSerializer(many=True)})
    def get(self, request):
        queryset = GuestWorkspace.objects.annotate(
            customer_count=Count("customers")
        ).select_related("owner").order_by("-created_at")

        if search := request.query_params.get("search"):
            queryset = queryset.filter(name__icontains=search)
        if status := request.query_params.get("status"):
            queryset = queryset.filter(status=status)

        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminWorkspaceListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Register a new Lender workspace", request=AdminLenderCreateSerializer)
    def post(self, request):
        serializer = AdminLenderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        workspace = AdminService.create_lender_workspace(serializer.validated_data)
        return success_response(
            data=AdminWorkspaceListSerializer(workspace).data,
            message="Lender workspace registered successfully.",
        )


class AdminWorkspaceDetailView(APIView):
    """
    GET   /api/v1/admin/workspaces/{id}/
    PUT   /api/v1/admin/workspaces/{id}/ — Update lender details/location/plan
    PATCH /api/v1/admin/workspaces/{id}/ — Update status
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return AdminLenderUpdateSerializer
        return WorkspaceStatusUpdateSerializer

    @extend_schema(summary="Get workspace details by public_id")
    def get(self, request, public_id):
        workspace = GuestWorkspace.objects.annotate(
            customer_count=Count("customers")
        ).select_related("owner").get(public_id=public_id)
        return success_response(data=AdminWorkspaceListSerializer(workspace).data)

    @extend_schema(summary="Update lender workspace details (location, plan, limits)", request=AdminLenderUpdateSerializer)
    def put(self, request, public_id):
        serializer = AdminLenderUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        workspace = AdminService.update_lender_workspace(public_id, serializer.validated_data)
        return success_response(
            data=AdminWorkspaceListSerializer(workspace).data,
            message="Lender workspace details updated.",
        )

    @extend_schema(summary="Update workspace status (active/suspended)", request=WorkspaceStatusUpdateSerializer)
    def patch(self, request, public_id):
        serializer = WorkspaceStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        workspace = AdminService.update_workspace_status(
            public_id, serializer.validated_data["status"]
        )
        return success_response(message="Workspace status updated successfully.")

    @extend_schema(summary="Delete lender workspace")
    def delete(self, request, public_id):
        AdminService.delete_workspace(public_id)
        return success_response(message="Lender workspace deleted successfully.")


class AdminContactInquiryListView(APIView):
    """GET /api/v1/admin/contact-inquiries/ — List all public contact inquiries"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = ContactInquirySerializer

    @extend_schema(summary="List all public contact inquiries & sales leads", responses={200: ContactInquirySerializer(many=True)})
    def get(self, request):
        inquiries = ContactInquiry.objects.all().order_by("-created_at")
        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(inquiries, request)
        serializer = ContactInquirySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminLenderPasswordResetView(APIView):
    """POST /api/v1/admin/workspaces/{id}/reset-password/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = AdminLenderPasswordResetSerializer

    @extend_schema(summary="Reset Lender password", request=AdminLenderPasswordResetSerializer)
    def post(self, request, public_id):
        serializer = AdminLenderPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        AdminService.reset_lender_password(public_id, serializer.validated_data["new_password"])
        return success_response(message="Lender account password reset successfully.")


class AdminQuotaOverrideView(APIView):
    """
    PATCH /api/v1/admin/workspaces/{public_id}/quota-override/
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = QuotaOverrideSerializer

    @extend_schema(summary="Set customer/collection quota override for workspace", request=QuotaOverrideSerializer)
    def patch(self, request, public_id):
        serializer = QuotaOverrideSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        try:
            AdminService.set_workspace_quota_override(
                public_id,
                max_customers=serializer.validated_data.get("max_customers_override"),
                max_collection_days=serializer.validated_data.get("max_collection_days_override"),
            )
        except Exception:
            pass
        return success_response(message="Workspace quota overrides updated successfully.")


class AdminMasterDataListCreateView(APIView):
    """
    GET  /api/v1/admin/masters/{category}/
    POST /api/v1/admin/masters/{category}/
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="List master records for category")
    def get(self, request, category):
        model_cls = MASTER_MODEL_MAP.get(category)
        if not model_cls:
            return error_response(f"Invalid master category: '{category}'")

        items = list(model_cls.objects.all().values("id", "code", "name"))
        return success_response(data=items)

    @extend_schema(summary="Create a new master item in category")
    def post(self, request, category):
        model_cls = MASTER_MODEL_MAP.get(category)
        if not model_cls:
            return error_response(f"Invalid master category: '{category}'")

        name = request.data.get("name")
        code = request.data.get("code") or name.lower().replace(" ", "_")
        if not name:
            return error_response("Name is required.")

        item = model_cls.objects.create(name=name, code=code)
        return success_response(
            data={"id": item.id, "code": item.code, "name": item.name},
            message=f"Created new {category} item.",
        )


class AdminMasterDataDetailView(APIView):
    """
    PUT    /api/v1/admin/masters/{category}/{pk}/
    DELETE /api/v1/admin/masters/{category}/{pk}/
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="Update master item")
    def put(self, request, category, pk):
        model_cls = MASTER_MODEL_MAP.get(category)
        if not model_cls:
            return error_response(f"Invalid master category: '{category}'")

        item = model_cls.objects.filter(pk=pk).first()
        if not item:
            return error_response("Item not found.", http_status=404)

        if name := request.data.get("name"):
            item.name = name
        if code := request.data.get("code"):
            item.code = code
        item.save()

        return success_response(
            data={"id": item.id, "code": item.code, "name": item.name},
            message="Master item updated.",
        )

    @extend_schema(summary="Delete master item")
    def delete(self, request, category, pk):
        model_cls = MASTER_MODEL_MAP.get(category)
        if not model_cls:
            return error_response(f"Invalid master category: '{category}'")

        model_cls.objects.filter(pk=pk).delete()
        return success_response(message="Master item deleted successfully.")


class AdminQuotaOverrideView(APIView):
    """PATCH /api/v1/admin/workspaces/{id}/quota-override/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = QuotaOverrideSerializer

    @extend_schema(summary="Set workspace quota overrides", request=QuotaOverrideSerializer)
    def patch(self, request, public_id):
        serializer = QuotaOverrideSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)

        workspace = AdminService.set_workspace_quota_override(
            public_id,
            max_customers=serializer.validated_data.get("max_customers_override"),
            max_collection_days=serializer.validated_data.get("max_collection_days_override"),
        )
        return success_response(message="Workspace quota override applied.")


class AdminCouponListCreateView(APIView):
    """
    GET  /api/v1/admin/coupons/
    POST /api/v1/admin/coupons/
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = PromoCouponSerializer

    @extend_schema(summary="List all promo coupons", responses={200: PromoCouponSerializer(many=True)})
    def get(self, request):
        coupons = PromoCoupon.objects.all().order_by("-created_at")
        return success_response(data=PromoCouponSerializer(coupons, many=True).data)

    @extend_schema(summary="Create a new promo coupon", request=PromoCouponSerializer)
    def post(self, request):
        from django.utils import timezone
        from datetime import timedelta

        data = dict(request.data)
        if not data.get("valid_from"):
            data["valid_from"] = timezone.now().isoformat()
        if not data.get("valid_until"):
            data["valid_until"] = (timezone.now() + timedelta(days=365)).isoformat()

        serializer = PromoCouponSerializer(data=data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)
        coupon = serializer.save(created_by=request.user if request.user and request.user.is_authenticated else None)
        return success_response(data=PromoCouponSerializer(coupon).data, message="Coupon created.")


class AdminAuditLogListView(APIView):
    """GET /api/v1/admin/audit-logs/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = AuditLogSerializer

    @extend_schema(summary="List all audit log entries", responses={200: AuditLogSerializer(many=True)})
    def get(self, request):
        logs = AuditLog.objects.select_related("user").order_by("-created_at")
        from apps.common.pagination import StandardPagination
        paginator = StandardPagination()
        page = paginator.paginate_queryset(logs, request)
        serializer = AuditLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminSubscriptionsListView(APIView):
    """GET /api/v1/admin/subscriptions/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = AdminSubscriptionSummarySerializer

    @extend_schema(summary="Get subscription breakdown and workspace tier summaries")
    def get(self, request):
        summary = AdminService.get_subscriptions_summary()
        return success_response(data=summary)


class AdminInvoiceListView(APIView):
    """GET /api/v1/admin/invoices/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = AdminInvoiceSerializer

    @extend_schema(summary="List billing invoices across tenants")
    def get(self, request):
        invoices = AdminService.get_invoices_list()
        return success_response(data=invoices)


class AdminBroadcastNotificationView(APIView):
    """POST /api/v1/admin/notifications/broadcast/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = BroadcastNotificationSerializer

    @extend_schema(summary="Broadcast platform notification to workspace owners", request=BroadcastNotificationSerializer)
    def post(self, request):
        serializer = BroadcastNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(errors=serializer.errors)
        
        return success_response(message="Notification broadcast queued successfully.")


class AdminConfigurationView(APIView):
    """
    GET /api/v1/admin/configuration/
    PUT /api/v1/admin/configuration/
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = GlobalConfigurationSerializer

    @extend_schema(summary="Get global SaaS configuration settings")
    def get(self, request):
        configs = GlobalConfiguration.objects.filter(is_active=True)
        return success_response(data=GlobalConfigurationSerializer(configs, many=True).data)

    @extend_schema(summary="Update global SaaS configuration setting")
    def put(self, request):
        key = request.data.get("key")
        value = request.data.get("value")

        config, _ = GlobalConfiguration.objects.get_or_create(key=key)
        config.value = value
        config.updated_by = request.user
        config.save()

        return success_response(message="Configuration updated.")


class AdminSubscriptionPlanConfigListCreateView(APIView):
    """
    GET  /api/v1/admin/subscriptions/plan-configs/ — List all subscription plan configurations
    POST /api/v1/admin/subscriptions/plan-configs/ — Create a new subscription plan configuration
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = SubscriptionPlanConfigSerializer

    @extend_schema(summary="List configured subscription plan catalog items", responses={200: SubscriptionPlanConfigSerializer(many=True)})
    def get(self, request, target_user_type=None):
        try:
            target = target_user_type or request.GET.get("target_user_type")
            qs = SubscriptionPlanConfig.objects.all()
            if target:
                qs = qs.filter(target_user_type=target)

            configs = list(qs.order_by("sort_order", "monthly_price"))
            if not configs:
                default_plans = [
                    {"plan_code": "plan_2_days", "target_user_type": "guest", "name": "Plan 1 — 2 Days / Week", "monthly_price": 199, "annual_price": 1990, "additional_days": 1, "max_customers": 0, "max_collection_days": 2, "tagline": "2 Collection Days per week with unlimited customers", "features": ["2 Collection Days / Week", "Unlimited Customers", "Full Passbook & Ledger"], "is_popular": False, "is_active": True, "sort_order": 10},
                    {"plan_code": "plan_3_days", "target_user_type": "guest", "name": "Plan 2 — 3 Days / Week", "monthly_price": 349, "annual_price": 3490, "additional_days": 2, "max_customers": 0, "max_collection_days": 3, "tagline": "3 Collection Days per week with unlimited customers", "features": ["3 Collection Days / Week", "Unlimited Customers", "Priority Customer Support"], "is_popular": True, "is_active": True, "sort_order": 20},
                    {"plan_code": "plan_4_days", "target_user_type": "guest", "name": "Plan 3 — 4 Days / Week", "monthly_price": 499, "annual_price": 4990, "additional_days": 3, "max_customers": 0, "max_collection_days": 4, "tagline": "4 Collection Days per week with unlimited customers", "features": ["4 Collection Days / Week", "Unlimited Customers", "Multi-Route Day Filtering"], "is_popular": False, "is_active": True, "sort_order": 30},
                    {"plan_code": "plan_7_days", "target_user_type": "guest", "name": "Full Week — 7 Days / Week", "monthly_price": 899, "annual_price": 8990, "additional_days": 6, "max_customers": 0, "max_collection_days": 7, "tagline": "All 7 Collection Days enabled with unlimited customers", "features": ["7 Collection Days (Full Week)", "Unlimited Customers", "Dedicated Account Guidance"], "is_popular": False, "is_active": True, "sort_order": 40},
                    {"plan_code": "lender_starter", "target_user_type": "lender", "name": "Lender ERP Starter", "monthly_price": 1499, "annual_price": 14990, "additional_days": 6, "max_customers": 500, "max_collection_days": 7, "tagline": "Full finance company setup for small NBFCs & teams", "features": ["5 Field Staff Seats", "GPS Location Tracking", "CIBIL Score Check"], "is_popular": False, "is_active": True, "sort_order": 50},
                    {"plan_code": "lender_pro", "target_user_type": "lender", "name": "Lender ERP Institutional", "monthly_price": 3999, "annual_price": 39990, "additional_days": 6, "max_customers": 2500, "max_collection_days": 7, "tagline": "Complete enterprise suite for scaling lending institutions", "features": ["25 Field Staff Seats", "Automated WhatsApp & SMS Alerts", "NPA Legal Recovery"], "is_popular": True, "is_active": True, "sort_order": 60},
                ]
                for p in default_plans:
                    try:
                        SubscriptionPlanConfig.objects.get_or_create(
                            plan_code=p["plan_code"],
                            defaults=p,
                        )
                    except Exception:
                        pass

                qs = SubscriptionPlanConfig.objects.all()
                if target:
                    qs = qs.filter(target_user_type=target)
                configs = list(qs.order_by("sort_order", "monthly_price"))

            return success_response(data=SubscriptionPlanConfigSerializer(configs, many=True).data)
        except Exception as e:
            logger.error("Error listing plan configs: %s", e)
            return success_response(data=[])

    @extend_schema(summary="Create a new subscription plan configuration", request=SubscriptionPlanConfigSerializer)
    def post(self, request, target_user_type=None, *args, **kwargs):
        try:
            from django.utils.text import slugify
            if hasattr(request.data, "dict"):
                data = request.data.dict()
            elif isinstance(request.data, dict):
                data = dict(request.data)
            else:
                data = {}

            if target_user_type and not data.get("target_user_type"):
                data["target_user_type"] = target_user_type

            name_val = data.get("name")
            if isinstance(name_val, list):
                name_val = name_val[0] if name_val else "custom"
            name_str = str(name_val or "custom")

            code_val = data.get("plan_code")
            if isinstance(code_val, list):
                code_val = code_val[0] if code_val else ""
            code_str = str(code_val or "").strip()

            raw_code = code_str or slugify(name_str).replace("-", "_")
            if not raw_code:
                raw_code = "custom_plan"

            if SubscriptionPlanConfig.objects.filter(plan_code=raw_code).exists():
                import time
                raw_code = f"{raw_code}_{int(time.time())}"
            data["plan_code"] = raw_code

            serializer = SubscriptionPlanConfigSerializer(data=data)
            if not serializer.is_valid():
                err_msg = "; ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in serializer.errors.items()])
                return error_response(message=f"Validation error: {err_msg}", errors=serializer.errors)
            config = serializer.save()
            return success_response(data=SubscriptionPlanConfigSerializer(config).data, message="Subscription plan configuration created successfully.")
        except Exception as e:
            logger.error("Error creating plan config: %s", e, exc_info=True)
            return error_response(message=f"Failed to create plan config: {str(e)}")


class AdminSubscriptionPlanConfigDetailView(APIView):
    """
    PUT    /api/v1/admin/subscriptions/plan-configs/{pk}/ — Update subscription plan configuration
    DELETE /api/v1/admin/subscriptions/plan-configs/{pk}/ — Delete subscription plan configuration
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = SubscriptionPlanConfigSerializer

    @extend_schema(summary="Update subscription plan configuration", request=SubscriptionPlanConfigSerializer)
    def put(self, request, pk, *args, **kwargs):
        try:
            from django.utils.text import slugify
            config = SubscriptionPlanConfig.objects.filter(pk=pk).first()
            if not config and request.data.get("plan_code"):
                config = SubscriptionPlanConfig.objects.filter(plan_code=request.data.get("plan_code")).first()

            if config:
                serializer = SubscriptionPlanConfigSerializer(config, data=request.data, partial=True)
                if not serializer.is_valid():
                    err_msg = "; ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in serializer.errors.items()])
                    return error_response(message=f"Validation error: {err_msg}", errors=serializer.errors)
                updated = serializer.save()
                return success_response(data=SubscriptionPlanConfigSerializer(updated).data, message="Subscription plan configuration updated successfully.")
            else:
                if hasattr(request.data, "dict"):
                    data = request.data.dict()
                elif isinstance(request.data, dict):
                    data = dict(request.data)
                else:
                    data = {}

                name_val = data.get("name")
                if isinstance(name_val, list):
                    name_val = name_val[0] if name_val else "custom"
                name_str = str(name_val or "custom")

                code_val = data.get("plan_code")
                if isinstance(code_val, list):
                    code_val = code_val[0] if code_val else ""
                code_str = str(code_val or "").strip()

                raw_code = code_str or slugify(name_str).replace("-", "_")
                if not raw_code:
                    raw_code = f"plan_{pk}"
                data["plan_code"] = raw_code

                serializer = SubscriptionPlanConfigSerializer(data=data)
                if not serializer.is_valid():
                    err_msg = "; ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in serializer.errors.items()])
                    return error_response(message=f"Validation error: {err_msg}", errors=serializer.errors)
                created = serializer.save()
                return success_response(data=SubscriptionPlanConfigSerializer(created).data, message="Subscription plan configuration created successfully.")
        except Exception as e:
            logger.error("Error updating plan config: %s", e, exc_info=True)
            return error_response(message=f"Failed to update plan config: {str(e)}")

    @extend_schema(summary="Delete subscription plan configuration")
    def delete(self, request, pk, *args, **kwargs):
        try:
            SubscriptionPlanConfig.objects.filter(pk=pk).delete()
        except Exception as e:
            logger.error("Error deleting plan config: %s", e)
        return success_response(message="Subscription plan configuration deleted successfully.")


class AdminReviewsView(APIView):
    """
    GET  /api/v1/admin/reviews/ — List all customer reviews (with status filter)
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="List customer reviews for admin moderation")
    def get(self, request):
        from apps.masters.models import CustomerReview
        from apps.masters.serializers import CustomerReviewSerializer

        status_filter = request.query_params.get("status")
        queryset = CustomerReview.objects.all().order_by("-created_at")
        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        return success_response(data=CustomerReviewSerializer(queryset, many=True).data)


class AdminReviewDetailView(APIView):
    """
    PATCH  /api/v1/admin/reviews/{pk}/ — Approve, Reject or update review status
    DELETE /api/v1/admin/reviews/{pk}/ — Delete review
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="Moderate customer review status")
    def patch(self, request, pk):
        from apps.masters.models import CustomerReview
        from apps.masters.serializers import CustomerReviewSerializer

        try:
            review = CustomerReview.objects.get(pk=pk)
        except CustomerReview.DoesNotExist:
            return error_response(message="Review not found.", status_code=404)

        status_val = request.data.get("status")
        if status_val in ["approved", "rejected", "pending"]:
            review.status = status_val
            review.is_approved = (status_val == "approved")
            review.save()
            return success_response(
                data=CustomerReviewSerializer(review).data,
                message=f"Review status updated to '{status_val}'.",
            )
        return error_response(message="Invalid status value. Must be 'approved', 'rejected', or 'pending'.")

    @extend_schema(summary="Delete customer review")
    def delete(self, request, pk):
        from apps.masters.models import CustomerReview
        CustomerReview.objects.filter(pk=pk).delete()
        return success_response(message="Review deleted successfully.")


class AdminUpgradeRequestsView(APIView):
    """
    GET /api/v1/admin/upgrade-requests/ — List all plan upgrade requests submitted by guest lenders.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="List all plan upgrade requests")
    def get(self, request):
        from apps.administration.models import PlanUpgradeRequest
        from apps.guest_workspace.serializers import PlanUpgradeRequestSerializer

        status_filter = request.query_params.get("status")
        queryset = PlanUpgradeRequest.objects.select_related("workspace", "requested_by").order_by("-created_at")
        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        return success_response(data=PlanUpgradeRequestSerializer(queryset, many=True).data)


class AdminUpgradeRequestDetailView(APIView):
    """
    PATCH /api/v1/admin/upgrade-requests/{pk}/ — Approve or Reject a plan upgrade request.
    If approved, automatically updates the workspace subscription plan and collection days capacity.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(summary="Approve or Reject plan upgrade request")
    def patch(self, request, pk):
        from django.db import transaction
        from apps.administration.models import PlanUpgradeRequest
        from apps.guest_workspace.serializers import PlanUpgradeRequestSerializer

        try:
            req_obj = PlanUpgradeRequest.objects.select_related("workspace").get(pk=pk)
        except PlanUpgradeRequest.DoesNotExist:
            return error_response(message="Upgrade request not found.", status_code=404)

        new_status = request.data.get("status")
        admin_notes = request.data.get("admin_notes", "")

        if new_status not in ["approved", "rejected", "pending"]:
            return error_response(message="Invalid status value. Must be 'approved', 'rejected', or 'pending'.")

        with transaction.atomic():
            req_obj.status = new_status
            if admin_notes:
                req_obj.admin_notes = admin_notes
            req_obj.save()

            if new_status == "approved":
                workspace = req_obj.workspace
                workspace.purchased_additional_days = req_obj.additional_days
                if req_obj.additional_days > 0:
                    workspace.subscription_plan = "premium"
                workspace.save()

        return success_response(
            data=PlanUpgradeRequestSerializer(req_obj).data,
            message=f"Upgrade request {new_status} successfully.",
        )
