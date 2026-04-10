"""Medico HMS — Orders Serializers"""
from rest_framework import serializers
from .models import ImagingOrder, LabOrder

class LabOrderSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="ordering_doctor.get_full_name", read_only=True)
    patient_mrn = serializers.CharField(source="encounter.patient.mrn", read_only=True)

    class Meta:
        model = LabOrder
        fields = ["id", "encounter", "patient_mrn", "ordering_doctor", "doctor_name",
                  "priority", "status", "cpt_code", "clinical_notes",
                  "specimen_type", "fasting_required", "created_at"]
        read_only_fields = ["id", "created_at"]

class ImagingOrderSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="ordering_doctor.get_full_name", read_only=True)
    patient_mrn = serializers.CharField(source="encounter.patient.mrn", read_only=True)

    class Meta:
        model = ImagingOrder
        fields = ["id", "encounter", "patient_mrn", "ordering_doctor", "doctor_name",
                  "priority", "status", "cpt_code", "clinical_notes",
                  "body_part", "modality", "contrast", "created_at"]
        read_only_fields = ["id", "created_at"]
