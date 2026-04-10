"""Medico HMS — Clinical Serializers"""
from rest_framework import serializers
from apps.codes.serializers import ICD10CodeSerializer
from .models import Allergy, Diagnosis, Encounter, ProgressNote, Vitals


class DiagnosisSerializer(serializers.ModelSerializer):
    icd10_detail = ICD10CodeSerializer(source="icd10_code", read_only=True)

    class Meta:
        model = Diagnosis
        fields = ["id", "encounter", "icd10_code", "icd10_detail", "diagnosis_type", "notes", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class VitalsSerializer(serializers.ModelSerializer):
    bmi = serializers.FloatField(read_only=True)
    blood_pressure = serializers.CharField(read_only=True)

    class Meta:
        model = Vitals
        fields = [
            "id", "encounter", "recorded_by",
            "temperature", "heart_rate",
            "blood_pressure_systolic", "blood_pressure_diastolic", "blood_pressure",
            "respiratory_rate", "oxygen_saturation",
            "weight", "height", "bmi", "pain_level", "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProgressNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = ProgressNote
        fields = [
            "id", "encounter", "author", "author_name", "note_type",
            "subjective", "objective", "assessment", "plan",
            "is_signed", "signed_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = [
            "id", "patient", "allergen", "allergy_type", "reaction",
            "severity", "onset_date", "status", "reported_by", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EncounterListSerializer(serializers.ModelSerializer):
    patient_mrn = serializers.CharField(source="patient.mrn", read_only=True)
    doctor_name = serializers.CharField(source="attending_doctor.get_full_name", read_only=True)
    length_of_stay = serializers.IntegerField(read_only=True)

    class Meta:
        model = Encounter
        fields = [
            "id", "patient", "patient_mrn", "attending_doctor", "doctor_name",
            "encounter_type", "admission_date", "discharge_date", "length_of_stay",
            "status", "chief_complaint", "created_at",
        ]


class EncounterDetailSerializer(serializers.ModelSerializer):
    diagnoses = DiagnosisSerializer(many=True, read_only=True)
    progress_notes = ProgressNoteSerializer(many=True, read_only=True)
    vitals = VitalsSerializer(many=True, read_only=True)
    patient_mrn = serializers.CharField(source="patient.mrn", read_only=True)
    doctor_name = serializers.CharField(source="attending_doctor.get_full_name", read_only=True)
    length_of_stay = serializers.IntegerField(read_only=True)

    class Meta:
        model = Encounter
        fields = [
            "id", "patient", "patient_mrn", "appointment",
            "attending_doctor", "doctor_name",
            "encounter_type", "admission_date", "discharge_date", "length_of_stay",
            "status", "chief_complaint", "discharge_summary", "discharge_disposition",
            "readmission_risk_score",
            "diagnoses", "progress_notes", "vitals",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
