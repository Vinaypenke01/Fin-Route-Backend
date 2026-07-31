"""
common/pagination.py

Standardized pagination classes used across all list endpoints.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Default pagination for all list endpoints.
    Supports ?page=N and ?page_size=N query parameters.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Data retrieved successfully.",
            "data": data,
            "errors": None,
            "meta": {
                "count": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
        })

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data": schema,
                "errors": {"nullable": True},
                "meta": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "num_pages": {"type": "integer"},
                        "current_page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                        "next": {"type": "string", "nullable": True},
                        "previous": {"type": "string", "nullable": True},
                    },
                },
            },
        }


class SmallPagination(PageNumberPagination):
    """
    Smaller page size for dashboard widgets and summary lists.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LargePagination(PageNumberPagination):
    """
    Larger page size for admin-facing lists and exports.
    """
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200
