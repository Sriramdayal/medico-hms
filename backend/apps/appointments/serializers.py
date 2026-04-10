"""Medico HMS — Appointment Serializers"""

from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from apps.patients.serializers import PatientListSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientListSerializer(source="patient", read_only=True)
    doctor_detail = UserSerializer(source="doctor", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "patient", "patient_detail", "doctor", "doctor_detail",
            "appointment_type", "scheduled_start", "scheduled_end",
            "status", "reason", "notes", "cancellation_reason",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "patient", "doctor", "appointment_type",
            "scheduled_start", "scheduled_end", "reason", "notes",
        ]

    def validate(self, data):
        if data["scheduled_start"] >= data["scheduled_end"]:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class AppointmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
