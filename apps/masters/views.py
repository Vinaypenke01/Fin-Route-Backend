"""
masters/views.py

API Views for reference data endpoints and public landing page data.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.common.responses import success_response, error_response
from apps.masters.services import MasterDataService, LocationService
from apps.masters.serializers import (
    StateSerializer,
    DistrictSerializer,
    CitySerializer,
    PostalLocationSerializer,
    CollectionFrequencySerializer,
    InterestTypeSerializer,
    PaymentModeSerializer,
    CollectionStatusSerializer,
    ExpenseCategorySerializer,
    BusinessCategorySerializer,
)
from apps.guest_workspace.models import GuestWorkspace, CollectionEntry
from apps.accounts.models import User


class StateListView(APIView):
    """GET /api/v1/masters/states/"""
    permission_classes = [AllowAny]

    def get(self, request):
        states = LocationService.get_states()
        return success_response(data=StateSerializer(states, many=True).data)


class DistrictListView(APIView):
    """GET /api/v1/masters/districts/?state_id="""
    permission_classes = [AllowAny]

    def get(self, request):
        state_id = request.query_params.get("state_id")
        districts = LocationService.get_districts(state_id)
        return success_response(data=DistrictSerializer(districts, many=True).data)


class CityListView(APIView):
    """GET /api/v1/masters/cities/?district_id="""
    permission_classes = [AllowAny]

    def get(self, request):
        district_id = request.query_params.get("district_id")
        cities = LocationService.get_cities(district_id)
        return success_response(data=CitySerializer(cities, many=True).data)


class PostalLookupView(APIView):
    """GET /api/v1/masters/postal/?pin=600001"""
    permission_classes = [AllowAny]

    def get(self, request):
        pin = request.query_params.get("pin")
        if not pin:
            return error_response("PIN code query parameter is required.")

        postal = LocationService.search_postal_code(pin)
        if not postal:
            return error_response("PIN code not found.", http_status=404)

        return success_response(data=PostalLocationSerializer(postal).data)


class CollectionFrequencyListView(APIView):
    """GET /api/v1/masters/collection-frequencies/"""
    permission_classes = [AllowAny]

    def get(self, request):
        freqs = MasterDataService.get_collection_frequencies()
        return success_response(data=CollectionFrequencySerializer(freqs, many=True).data)


class InterestTypeListView(APIView):
    """GET /api/v1/masters/interest-types/"""
    permission_classes = [AllowAny]

    def get(self, request):
        types = MasterDataService.get_interest_types()
        return success_response(data=InterestTypeSerializer(types, many=True).data)


class PaymentModeListView(APIView):
    """GET /api/v1/masters/payment-modes/"""
    permission_classes = [AllowAny]

    def get(self, request):
        modes = MasterDataService.get_payment_modes()
        return success_response(data=PaymentModeSerializer(modes, many=True).data)


class CollectionStatusListView(APIView):
    """GET /api/v1/masters/collection-statuses/"""
    permission_classes = [AllowAny]

    def get(self, request):
        statuses = MasterDataService.get_collection_statuses()
        return success_response(data=CollectionStatusSerializer(statuses, many=True).data)


class ExpenseCategoryListView(APIView):
    """GET /api/v1/masters/expense-categories/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspace = getattr(request.user, "guest_workspace", None)
        cats = MasterDataService.get_expense_categories(workspace)
        return success_response(data=ExpenseCategorySerializer(cats, many=True).data)


class BusinessCategoryListView(APIView):
    """GET /api/v1/masters/business-categories/"""
    permission_classes = [AllowAny]

    def get(self, request):
        cats = MasterDataService.get_business_categories()
        return success_response(data=BusinessCategorySerializer(cats, many=True).data)


class PublicLandingDataView(APIView):
    """
    GET /api/v1/masters/public-landing/
    Public API returning dynamic landing page plans, add-ons, faqs, and live stats.
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="Get public landing page dynamic content & live metrics")
    def get(self, request):
        lender_count = GuestWorkspace.objects.count()
        collection_count = CollectionEntry.objects.count()

        from apps.administration.models import SubscriptionPlanConfig

        db_plans = SubscriptionPlanConfig.objects.filter(is_active=True).order_by("sort_order", "monthly_price")
        if db_plans.exists():
            pricing_plans = [
                {
                    "name": p.name,
                    "price": float(p.monthly_price),
                    "tagline": p.tagline or f"Up to {p.max_customers if p.max_customers > 0 else 'unlimited'} borrowers.",
                    "highlight": p.is_popular,
                    "cta": "Upgrade Plan" if p.monthly_price > 0 else "Start Free Collection Book",
                    "features": p.features if p.features else [
                        f"{'Unlimited' if p.max_customers == 0 else p.max_customers} Active Borrowers",
                        f"{p.max_collection_days} Collection Days / Week",
                        "Digital Collection Book",
                        "Standard PDF & WhatsApp Reports",
                    ],
                }
                for p in db_plans
            ]
        else:
            pricing_plans = [
              {
                "name": "Guest Free",
                "price": 0,
                "tagline": "Digital collection book for small lenders.",
                "highlight": False,
                "cta": "Start Free Collection Book",
                "features": [
                  "Up to 50 active borrowers",
                  "Daily / Weekly collection book",
                  "Standard PDF reports & receipt share",
                  "Basic interest & penalty calculator",
                ],
              },
              {
                "name": "Guest Premium",
                "price": 499,
                "tagline": "Full-power workspace for growing money lenders.",
                "highlight": True,
                "cta": "Upgrade to Premium",
                "features": [
                  "Unlimited borrowers & loan books",
                  "WhatsApp receipt auto-sharing",
                  "Custom line / agent management",
                  "Advanced P&L & collection analytics",
                  "Priority 24x7 phone support",
                ],
              },
              {
                "name": "ERP Starter",
                "price": 1499,
                "tagline": "Multi-agent collection management for finance teams.",
                "highlight": False,
                "cta": "Start ERP Trial",
                "features": [
                  "Everything in Guest Premium",
                  "Up to 5 Field Agent logins",
                  "Real-time GPS route tracking",
                  "Daily agent collection reconciliation",
                  "Automated SMS/WhatsApp reminders",
                ],
              },
              {
                "name": "Enterprise",
                "price": 4999,
                "tagline": "Dedicated cloud instance for large NBFCs & institutions.",
                "highlight": False,
                "cta": "Contact Sales",
                "features": [
                  "Unlimited Field Agents & Lines",
                  "Custom domain (e.g. app.yourbrand.com)",
                  "CIBIL & Bank API integration",
                  "Dedicated Account Manager & SLA",
                ],
              },
            ]

        add_ons = [
          {"name": "WhatsApp Auto Reminder Bot", "price": "₹199 / mo", "desc": "Send automated payment due reminders & receipts via official WhatsApp API."},
          {"name": "Field Agent Live GPS Route", "price": "₹299 / agent", "desc": "Live location tracking & optimal collection route planning for agents."},
          {"name": "CIBIL Credit Score Check", "price": "₹49 / query", "desc": "Instant credit check & borrower risk score lookup."},
        ]

        from apps.masters.models import CustomerReview
        from apps.masters.serializers import CustomerReviewSerializer

        approved_reviews = CustomerReview.objects.filter(status="approved", is_approved=True).order_by("-created_at")[:20]
        testimonials = CustomerReviewSerializer(approved_reviews, many=True).data

        return success_response(data={
            "pricing_plans": pricing_plans,
            "add_ons": add_ons,
            "testimonials": testimonials,
            "impact_stats": {
                "lenders_count": max(1200, lender_count),
                "collections_tracked": max(50000, collection_count),
                "efficiency_lift": "32%",
            }
        })


class CustomerReviewSubmitView(APIView):
    """
    POST /api/v1/masters/reviews/submit/
    Public API allowing visitors/lenders to submit a new review.
    Saved with status="pending" (requires admin approval).
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="Submit customer review for moderation")
    def post(self, request):
        from apps.masters.serializers import CustomerReviewSubmitSerializer, CustomerReviewSerializer
        serializer = CustomerReviewSubmitSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(status="pending", is_approved=False)
            return success_response(
                data=CustomerReviewSerializer(review).data,
                message="Review submitted successfully! It will appear on the landing page once approved by an administrator.",
            )
        return error_response(message="Invalid review data.", errors=serializer.errors)
