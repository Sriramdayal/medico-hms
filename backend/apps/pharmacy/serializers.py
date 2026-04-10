"""Medico HMS — Pharmacy Serializers"""
from rest_framework import serializers
from .models import Drug, DrugAdministration, Prescription


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = [
            "id", "name", "generic_name", "ndc_code", "drug_class",
            "form", "strength", "manufacturer", "requires_prescription",
            "is_controlled", "contraindications", "side_effects", "is_active",
        ]


class DrugAdministrationSerializer(serializers.ModelSerializer):
    administered_by_name = serializers.CharField(source="administered_by.get_full_name", read_only=True)

    class Meta:
        model = DrugAdministration
        fields = [
            "id", "prescription", "administered_by", "administered_by_name",
            "administered_at", "dose_given", "route", "site",
            "notes", "patient_response", "was_refused", "refusal_reason", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PrescriptionSerializer(serializers.ModelSerializer):
    drug_detail = DrugSerializer(source="drug", read_only=True)
    doctor_name = serializers.CharField(source="prescribing_doctor.get_full_name", read_only=True)
    administrations = DrugAdministrationSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id", "encounter", "patient", "prescribing_doctor", "doctor_name",
            "drug", "drug_detail", "dosage", "frequency", "route",
            "duration_days", "quantity", "refills_allowed", "instructions",
            "status", "discontinued_reason", "administrations",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
