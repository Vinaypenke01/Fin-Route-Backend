"""
guest_workspace/urls.py — URL routing for Guest Workspace app shell.
Mounted at: /api/v1/app/
"""

from django.urls import path
from apps.guest_workspace.views import (
    WorkspaceDetailView,
    DashboardView,
    WeeklySummaryView,
    CustomerListCreateView,
    CustomerDetailView,
    CustomerCollectionsView,
    CollectionListCreateView,
    CollectionBatchView,
    CollectionDetailView,
    ExpenseListCreateView,
    ExpenseDetailView,
    ReportsCollectionsView,
    ReportsCustomersView,
    ReportsExpensesView,
    ReportsExportView,
    CalculatorView,
    UpgradeView,
    SubmitUpgradeRequestView,
    WorkspaceDataBackupView,
    CapitalEntryView,
    CapitalEntryDetailView,
    DailyCashReconciliationView,
    SendRouteClosureReportView,
    TriggerDailyRouteEmailsView,
    LineListCreateView,
    LineDetailView,
    AvailablePortionsView,
)

urlpatterns = [
    # Lines (Routes)
    path("lines/", LineListCreateView.as_view(), name="app-line-list-create"),
    path("lines/available-portions/", AvailablePortionsView.as_view(), name="app-line-available-portions"),
    path("lines/<uuid:line_public_id>/", LineDetailView.as_view(), name="app-line-detail"),
    # Workspace Settings
    path("workspace/", WorkspaceDetailView.as_view(), name="app-workspace"),

    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="app-dashboard"),
    path("dashboard/weekly-summary/", WeeklySummaryView.as_view(), name="app-weekly-summary"),

    # Customers
    path("customers/", CustomerListCreateView.as_view(), name="app-customer-list-create"),
    path("customers/<uuid:public_id>/", CustomerDetailView.as_view(), name="app-customer-detail"),
    path("customers/<uuid:public_id>/collections/", CustomerCollectionsView.as_view(), name="app-customer-collections"),

    # Collections
    path("collections/", CollectionListCreateView.as_view(), name="app-collection-list-create"),
    path("collections/batch/", CollectionBatchView.as_view(), name="app-collection-batch"),
    path("collections/<uuid:public_id>/", CollectionDetailView.as_view(), name="app-collection-detail"),

    # Expenses
    path("expenses/", ExpenseListCreateView.as_view(), name="app-expense-list-create"),
    path("expenses/<uuid:public_id>/", ExpenseDetailView.as_view(), name="app-expense-detail"),

    # Capital & Cash Reconciliation
    path("capital/", CapitalEntryView.as_view(), name="app-capital-list-create"),
    path("capital/<uuid:public_id>/", CapitalEntryDetailView.as_view(), name="app-capital-detail"),
    path("cash-reconciliation/", DailyCashReconciliationView.as_view(), name="app-cash-reconciliation"),
    path("cash-reconciliation/send-report/", SendRouteClosureReportView.as_view(), name="app-cash-reconciliation-send-report"),

    # Reports
    path("reports/collections/", ReportsCollectionsView.as_view(), name="app-reports-collections"),
    path("reports/customers/", ReportsCustomersView.as_view(), name="app-reports-customers"),
    path("reports/expenses/", ReportsExpensesView.as_view(), name="app-reports-expenses"),
    path("reports/export/", ReportsExportView.as_view(), name="app-reports-export"),
    path("reports/trigger-daily-emails/", TriggerDailyRouteEmailsView.as_view(), name="app-reports-trigger-daily-emails"),

    # Calculator, Upgrade & Backup
    path("calculator/", CalculatorView.as_view(), name="app-calculator"),
    path("upgrade/", UpgradeView.as_view(), name="app-upgrade"),
    path("upgrade/plans/", UpgradeView.as_view(), name="app-upgrade-plans"),
    path("upgrade/submit/", SubmitUpgradeRequestView.as_view(), name="app-upgrade-submit"),
    path("backup/download/", WorkspaceDataBackupView.as_view(), name="app-backup-download"),
]
