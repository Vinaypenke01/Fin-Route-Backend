"""
masters/serializers.py

Serializers for reference data tables.
"""

from rest_framework import serializers
from apps.masters.models import (
    State,
    District,
    City,
    PostalLocation,
    CollectionFrequency,
    InterestType,
    PaymentMode,
    CollectionStatus,
    ExpenseCategory,
    BusinessCategory,
    CustomerReview,
)


class StateSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = State
        fields = ["id", "public_id", "name", "code", "country_code"]


class DistrictSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)

    class Meta:
        model = District
        fields = ["id", "public_id", "state", "state_name", "name", "code"]


class CitySerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = City
        fields = ["id", "public_id", "district", "district_name", "name", "location_type"]


class PostalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalLocation
        fields = ["postal_code", "post_office_name", "branch_type", "district_name", "state_name"]


class CollectionFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionFrequency
        fields = ["id", "code", "name", "description", "sort_order"]


class InterestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestType
        fields = ["id", "code", "name", "description"]


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ["id", "code", "name", "description", "sort_order"]


class CollectionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionStatus
        fields = ["id", "code", "name", "requires_reason", "affects_outstanding", "sort_order"]


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ["id", "code", "name", "is_system"]


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ["id", "code", "name", "description"]


class CustomerReviewSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = CustomerReview
        fields = [
            "id",
            "public_id",
            "author_name",
            "business_name",
            "role_title",
            "rating",
            "review_text",
            "avatar_url",
            "status",
            "is_approved",
            "created_at",
        ]


class CustomerReviewSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = ["author_name", "business_name", "role_title", "rating", "review_text", "avatar_url"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
