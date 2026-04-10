"""Medico HMS — Pharmacy Views"""
from rest_framework import generics, permissions
from .models import Drug, DrugAdministration, Prescription
from .serializers import DrugSerializer, DrugAdministrationSerializer, PrescriptionSerializer


class DrugListCreateView(generics.ListCreateAPIView):
    queryset = Drug.objects.filter(is_active=True)
    serializer_class = DrugSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "generic_name", "ndc_code", "drug_class"]
    filterset_fields = ["form", "requires_prescription", "is_controlled"]


class DrugDetailView(generics.RetrieveUpdateAPIView):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer
    permission_classes = [permissions.IsAuthenticated]


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "patient", "encounter"]

    def get_queryset(self):
        return Prescription.objects.select_related("drug", "prescribing_doctor", "patient").all()

    def perform_create(self, serializer):
        serializer.save(prescribing_doctor=self.request.user, created_by=self.request.user)


class PrescriptionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.select_related("drug", "prescribing_doctor").prefetch_related("administrations").all()


class DrugAdministrationListCreateView(generics.ListCreateAPIView):
    serializer_class = DrugAdministrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DrugAdministration.objects.filter(prescription_id=self.kwargs["prescription_id"])

    def perform_create(self, serializer):
        serializer.save(
            prescription_id=self.kwargs["prescription_id"],
            administered_by=self.request.user,
            created_by=self.request.user,
        )
