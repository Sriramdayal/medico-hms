"""
Medico HMS — Patient Serializers
"""

from rest_framework import serializers

from .models import EmergencyContact, Insurance, Patient


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "name", "relationship", "phone", "email", "is_primary"]


class InsuranceSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Insurance
        fields = [
            "id", "provider_name", "policy_number", "group_number",
            "plan_type", "effective_date", "expiry_date",
            "is_primary", "subscriber_name", "subscriber_relationship",
            "is_active",
        ]


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no encrypted fields exposed in full)."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "mrn", "first_name", "last_name", "full_name",
            "date_of_birth", "age", "gender", "blood_type",
            "status", "created_at",
        ]


class PatientDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views, includes related data."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    insurances = InsuranceSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id", "mrn", "first_name", "last_name", "full_name",
            "date_of_birth", "age", "gender", "blood_type",
            "ssn", "email", "phone",
            "address_line_1", "address_line_2", "city", "state",
            "postal_code", "country",
            "marital_status", "occupation", "preferred_language",
            "status",
            "emergency_contacts", "insurances",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "mrn", "created_at", "updated_at"]


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for patient registration."""

    class Meta:
        model = Patient
        fields = [
            "first_name", "last_name", "date_of_birth", "gender",
            "blood_type", "ssn", "email", "phone",
            "address_line_1", "address_line_2", "city", "state",
            "postal_code", "country",
            "marital_status", "occupation", "preferred_language",
        ]
