"""
accounts/urls/account_urls.py — Account management URL routes.
Mounted at: /api/v1/accounts/
"""

from django.urls import path
from apps.accounts.views import ContactInquiryCreateView

urlpatterns = [
    path("contact-us/", ContactInquiryCreateView.as_view(), name="contact-us"),
]
