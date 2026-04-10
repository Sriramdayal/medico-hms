"""
Medico HMS — Patient Views
API endpoints for patient management (MPI).
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.core.models import AuditLog
from apps.core.permissions import IsClinicalStaff

from .models import EmergencyContact, Insurance, Patient
from .serializers import (
    EmergencyContactSerializer,
    InsuranceSerializer,
    PatientCreateSerializer,
    PatientDetailSerializer,
    PatientListSerializer,
)


class PatientListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/patients/          — List patients (search by name, MRN)
    POST /api/v1/patients/          — Register a new patient
    """

    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["mrn", "first_name", "last_name"]
    filterset_fields = ["status", "gender"]
    ordering_fields = ["created_at", "mrn"]

    def get_queryset(self):
        return Patient.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PatientCreateSerializer
        return PatientListSerializer

    def perform_create(self, serializer):
        patient = serializer.save(created_by=self.request.user)
        AuditLog.log(
            user=self.request.user,
            action="CREATE",
            resource_type="Patient",
            resource_id=str(patient.pk),
            request=self.request,
        )


class PatientDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/patients/{id}/    — Patient detail with full history
    PATCH /api/v1/patients/{id}/    — Update patient demographics
    """

    serializer_class = PatientDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return Patient.objects.prefetch_related("emergency_contacts", "insurances")

    def perform_update(self, serializer):
        patient = serializer.save(updated_by=self.request.user)
        AuditLog.log(
            user=self.request.user,
            action="UPDATE",
            resource_type="Patient",
            resource_id=str(patient.pk),
            request=self.request,
        )


class PatientByMRNView(generics.RetrieveAPIView):
    """
    GET /api/v1/patients/mrn/{mrn}/ — Lookup patient by MRN
    """

    serializer_class = PatientDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "mrn"

    def get_queryset(self):
        return Patient.objects.prefetch_related("emergency_contacts", "insurances")


class EmergencyContactListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/patients/{patient_id}/emergency-contacts/
    POST /api/v1/patients/{patient_id}/emergency-contacts/
    """

    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(patient_id=self.kwargs["patient_id"])

    def perform_create(self, serializer):
        serializer.save(
            patient_id=self.kwargs["patient_id"],
            created_by=self.request.user,
        )


class InsuranceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/patients/{patient_id}/insurance/
    POST /api/v1/patients/{patient_id}/insurance/
    """

    serializer_class = InsuranceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Insurance.objects.filter(patient_id=self.kwargs["patient_id"])

    def perform_create(self, serializer):
        serializer.save(
            patient_id=self.kwargs["patient_id"],
            created_by=self.request.user,
        )
