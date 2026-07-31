"""
masters/urls.py — URL routing for masters reference data.
Mounted at: /api/v1/masters/
"""

from django.urls import path
from apps.masters.views import (
    StateListView,
    DistrictListView,
    CityListView,
    PostalLookupView,
    CollectionFrequencyListView,
    InterestTypeListView,
    PaymentModeListView,
    CollectionStatusListView,
    ExpenseCategoryListView,
    BusinessCategoryListView,
    PublicLandingDataView,
    CustomerReviewSubmitView,
)

urlpatterns = [
    # Location
    path("states/", StateListView.as_view(), name="master-states"),
    path("districts/", DistrictListView.as_view(), name="master-districts"),
    path("cities/", CityListView.as_view(), name="master-cities"),
    path("postal/", PostalLookupView.as_view(), name="master-postal"),

    # Public Landing Page Data & Review Submission
    path("public-landing/", PublicLandingDataView.as_view(), name="master-public-landing"),
    path("reviews/submit/", CustomerReviewSubmitView.as_view(), name="master-reviews-submit"),

    # Domain Reference Data
    path("collection-frequencies/", CollectionFrequencyListView.as_view(), name="master-collection-frequencies"),
    path("interest-types/", InterestTypeListView.as_view(), name="master-interest-types"),
    path("payment-modes/", PaymentModeListView.as_view(), name="master-payment-modes"),
    path("collection-statuses/", CollectionStatusListView.as_view(), name="master-collection-statuses"),
    path("expense-categories/", ExpenseCategoryListView.as_view(), name="master-expense-categories"),
    path("business-categories/", BusinessCategoryListView.as_view(), name="master-business-categories"),
]
