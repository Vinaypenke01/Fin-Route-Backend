"""
masters/services/location_service.py

LocationService handles location data lookup and PIN code searches.
"""

import logging
from apps.masters.models import State, District, City, PostalLocation

logger = logging.getLogger(__name__)


class LocationService:
    """
    Location reference data lookups.
    """

    @staticmethod
    def get_states():
        """Get active states list."""
        return State.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def get_districts(state_id: str = None):
        """Get districts, optionally filtered by state public_id or integer PK."""
        queryset = District.objects.filter(is_active=True).select_related("state")
        if state_id:
            if str(state_id).isdigit():
                queryset = queryset.filter(state_id=state_id)
            else:
                queryset = queryset.filter(state__public_id=state_id)
        return queryset.order_by("name")

    @staticmethod
    def get_cities(district_id: str = None):
        """Get cities/towns, optionally filtered by district public_id or PK."""
        queryset = City.objects.filter(is_active=True).select_related("district")
        if district_id:
            if str(district_id).isdigit():
                queryset = queryset.filter(district_id=district_id)
            else:
                queryset = queryset.filter(district__public_id=district_id)
        return queryset.order_by("name")

    @staticmethod
    def search_postal_code(pin_code: str):
        """
        Lookup location details by 6-digit PIN code.
        """
        return PostalLocation.objects.filter(postal_code=pin_code).first()
