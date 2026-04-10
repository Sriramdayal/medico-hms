"""
Medico HMS — Standardized Pagination
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    """Standard pagination for all list endpoints."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeResultsPagination(PageNumberPagination):
    """Larger pagination for reference data (ICD-10 codes, etc.)."""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500
