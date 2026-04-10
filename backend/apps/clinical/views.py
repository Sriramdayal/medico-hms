"""Medico HMS — Clinical Views"""
from rest_framework import generics, permissions
from .models import Allergy, Diagnosis, Encounter, ProgressNote, Vitals
from .serializers import (
    AllergySerializer, DiagnosisSerializer, EncounterDetailSerializer,
    EncounterListSerializer, ProgressNoteSerializer, VitalsSerializer,
)


class EncounterListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "encounter_type", "patient", "attending_doctor"]
    ordering_fields = ["admission_date", "created_at"]

    def get_queryset(self):
        return Encounter.objects.select_related("patient", "attending_doctor").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EncounterDetailSerializer
        return EncounterListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EncounterDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = EncounterDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Encounter.objects.prefetch_related("diagnoses", "progress_notes", "vitals").all()


class DiagnosisListCreateView(generics.ListCreateAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Diagnosis.objects.filter(encounter_id=self.kwargs["encounter_id"])

    def perform_create(self, serializer):
        serializer.save(encounter_id=self.kwargs["encounter_id"], created_by=self.request.user)


class ProgressNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = ProgressNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgressNote.objects.filter(encounter_id=self.kwargs["encounter_id"])

    def perform_create(self, serializer):
        serializer.save(encounter_id=self.kwargs["encounter_id"], author=self.request.user, created_by=self.request.user)


class ProgressNoteDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProgressNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgressNote.objects.all()


class VitalsListCreateView(generics.ListCreateAPIView):
    serializer_class = VitalsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vitals.objects.filter(encounter_id=self.kwargs["encounter_id"])

    def perform_create(self, serializer):
        serializer.save(encounter_id=self.kwargs["encounter_id"], recorded_by=self.request.user, created_by=self.request.user)


class AllergyListCreateView(generics.ListCreateAPIView):
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Allergy.objects.filter(patient_id=self.kwargs["patient_id"])

    def perform_create(self, serializer):
        serializer.save(patient_id=self.kwargs["patient_id"], reported_by=self.request.user, created_by=self.request.user)
