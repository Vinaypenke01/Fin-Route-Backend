"""
Root URL configuration for Finance Business ERP Backend.
All API endpoints are versioned under /api/v1/.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path("django-admin/", admin.site.urls),

    # API v1 — Authentication & Accounts
    path("api/v1/auth/", include("apps.accounts.urls.auth_urls")),
    path("api/v1/accounts/", include("apps.accounts.urls.account_urls")),

    # API v1 — Masters (Reference Data)
    path("api/v1/masters/", include("apps.masters.urls")),

    # API v1 — Guest Workspace (App Shell)
    path("api/v1/app/", include("apps.guest_workspace.urls")),

    # API v1 — Super Admin Console
    path("api/v1/admin/", include("apps.administration.urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
