"""
Medico HMS — Codes Views
Read-only API endpoints for medical reference codes.
"""

from rest_framework import generics, permissions

from apps.core.pagination import LargeResultsPagination

from .models import CPTCode, ICD10Code
from .serializers import CPTCodeSerializer, ICD10CodeSerializer


class ICD10CodeListView(generics.ListAPIView):
    """
    GET /api/v1/codes/icd10/
    List and search ICD-10 codes.
    """

    queryset = ICD10Code.objects.all()
    serializer_class = ICD10CodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsPagination
    search_fields = ["code", "description", "category"]
    filterset_fields = ["category", "is_billable", "version_year"]


class ICD10CodeDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/codes/icd10/{id}/
    Retrieve a specific ICD-10 code.
    """

    queryset = ICD10Code.objects.all()
    serializer_class = ICD10CodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class CPTCodeListView(generics.ListAPIView):
    """
    GET /api/v1/codes/cpt/
    List and search CPT codes.
    """

    queryset = CPTCode.objects.all()
    serializer_class = CPTCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsPagination
    search_fields = ["code", "description", "category"]
    filterset_fields = ["category", "version_year"]


class CPTCodeDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/codes/cpt/{id}/
    Retrieve a specific CPT code.
    """

    queryset = CPTCode.objects.all()
    serializer_class = CPTCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
