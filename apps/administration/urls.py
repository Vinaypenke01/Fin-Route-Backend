"""
administration/urls.py — URL routing for Super Admin Console.
Mounted at: /api/v1/admin/
"""

from django.urls import path
from apps.administration.views import (
    AdminDashboardView,
    AdminSystemHealthView,
    AdminWorkspaceListView,
    AdminWorkspaceDetailView,
    AdminContactInquiryListView,
    AdminLenderPasswordResetView,
    AdminQuotaOverrideView,
    AdminMasterDataListCreateView,
    AdminMasterDataDetailView,
    AdminCouponListCreateView,
    AdminAuditLogListView,
    AdminConfigurationView,
    AdminSubscriptionsListView,
    AdminInvoiceListView,
    AdminBroadcastNotificationView,
    AdminSubscriptionPlanConfigListCreateView,
    AdminSubscriptionPlanConfigDetailView,
    AdminReviewsView,
    AdminReviewDetailView,
    AdminUpgradeRequestsView,
    AdminUpgradeRequestDetailView,
)

urlpatterns = [
    # Dashboard & Infrastructure
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("system-health/", AdminSystemHealthView.as_view(), name="admin-system-health"),

    # Plan Upgrade Requests Moderation
    path("upgrade-requests/", AdminUpgradeRequestsView.as_view(), name="admin-upgrade-requests-list"),
    path("upgrade-requests/<int:pk>/", AdminUpgradeRequestDetailView.as_view(), name="admin-upgrade-requests-detail"),

    # Customer Reviews Moderation
    path("reviews/", AdminReviewsView.as_view(), name="admin-reviews-list"),
    path("reviews/<int:pk>/", AdminReviewDetailView.as_view(), name="admin-reviews-detail"),

    # Tenant / Workspace Management
    path("workspaces/", AdminWorkspaceListView.as_view(), name="admin-workspace-list"),
    path("workspaces/<str:public_id>/", AdminWorkspaceDetailView.as_view(), name="admin-workspace-detail"),
    path("workspaces/<str:public_id>/reset-password/", AdminLenderPasswordResetView.as_view(), name="admin-lender-reset-password"),
    path("workspaces/<str:public_id>/quota-override/", AdminQuotaOverrideView.as_view(), name="admin-quota-override"),

    # Contact Inquiries / Sales Leads
    path("contact-inquiries/", AdminContactInquiryListView.as_view(), name="admin-contact-inquiries"),

    # Master Data Management
    path("masters/<str:category>/", AdminMasterDataListCreateView.as_view(), name="admin-masters-list"),
    path("masters/<str:category>/<int:pk>/", AdminMasterDataDetailView.as_view(), name="admin-masters-detail"),

    # Subscriptions & Billing (Lender Plans)
    path("subscriptions/", AdminSubscriptionsListView.as_view(), name="admin-subscriptions"),
    path("subscriptions/plan-configs/", AdminSubscriptionPlanConfigListCreateView.as_view(), name="admin-subscription-plan-configs-list"),
    path("subscriptions/plan-configs/<int:pk>/", AdminSubscriptionPlanConfigDetailView.as_view(), name="admin-subscription-plan-configs-detail"),

    # Guest User Day-Wise Plans Screen
    path("guest-plans/", AdminSubscriptionPlanConfigListCreateView.as_view(), {"target_user_type": "guest"}, name="admin-guest-plans-list"),
    path("guest-plans/<int:pk>/", AdminSubscriptionPlanConfigDetailView.as_view(), name="admin-guest-plans-detail"),
    path("invoices/", AdminInvoiceListView.as_view(), name="admin-invoices"),

    # Broadcast Notifications
    path("notifications/broadcast/", AdminBroadcastNotificationView.as_view(), name="admin-broadcast-notification"),

    # Coupons & Discounts
    path("coupons/", AdminCouponListCreateView.as_view(), name="admin-coupons"),

    # Audit Logs & Configuration
    path("audit-logs/", AdminAuditLogListView.as_view(), name="admin-audit-logs"),
    path("configuration/", AdminConfigurationView.as_view(), name="admin-configuration"),
    path("configuration/guest-limits/", AdminConfigurationView.as_view(), name="admin-guest-limits"),
]
