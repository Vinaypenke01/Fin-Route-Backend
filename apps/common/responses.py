"""
common/responses.py

Standardized API response helpers used across all views.
Every view must use these helpers to ensure consistent response shapes.

Response shape:
{
    "success": true | false,
    "message": "...",
    "data": {...} | [...] | null,
    "errors": {...} | null,
    "meta": {...} | null   (pagination metadata)
}
"""

from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success.", http_status=status.HTTP_200_OK) -> Response:
    """
    Return a standardized success response.

    Args:
        data: The response payload (dict, list, or None).
        message: Human-readable success message.
        http_status: HTTP status code (default 200).

    Returns:
        DRF Response with standardized success envelope.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
        },
        status=http_status,
    )


def created_response(data=None, message="Created successfully.") -> Response:
    """
    Return a standardized 201 Created response.
    """
    return success_response(data=data, message=message, http_status=status.HTTP_201_CREATED)


def error_response(
    message="An error occurred.",
    errors=None,
    http_status=status.HTTP_400_BAD_REQUEST,
) -> Response:
    """
    Return a standardized error response.

    Args:
        message: Human-readable error message.
        errors: Field-level error details dict.
        http_status: HTTP status code (default 400).

    Returns:
        DRF Response with standardized error envelope.
    """
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors or {},
        },
        status=http_status,
    )


def paginated_response(page, serializer, message="Data retrieved successfully.") -> Response:
    """
    Return a standardized paginated response.
    Used with DRF pagination inside ListAPIViews.

    Args:
        page: Paginated queryset page.
        serializer: Serializer instance with `many=True` context.
        message: Human-readable success message.

    Returns:
        DRF Response with standardized success envelope + pagination meta.
    """
    return Response(
        {
            "success": True,
            "message": message,
            "data": serializer.data,
            "errors": None,
            "meta": {
                "count": page.paginator.count,
                "num_pages": page.paginator.num_pages,
                "current_page": page.number,
                "next": page.has_next(),
                "previous": page.has_previous(),
            },
        },
        status=status.HTTP_200_OK,
    )
