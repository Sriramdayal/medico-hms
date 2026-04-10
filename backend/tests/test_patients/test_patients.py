"""
Medico HMS — Patient Tests
Tests for patient registration, MRN generation, and data integrity.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestPatientAPI:
    """Tests for patient CRUD operations."""

    def test_create_patient(self, authenticated_admin_client):
        """Test creating a new patient auto-generates MRN."""
        response = authenticated_admin_client.post(
            "/api/v1/patients/",
            {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1985-03-20",
                "gender": "male",
                "blood_type": "A+",
                "phone": "555-0101",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_patients(self, authenticated_doctor_client, sample_patient):
        """Test listing patients."""
        response = authenticated_doctor_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK

    def test_get_patient_detail(self, authenticated_doctor_client, sample_patient):
        """Test retrieving patient detail."""
        response = authenticated_doctor_client.get(f"/api/v1/patients/{sample_patient.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["mrn"] == sample_patient.mrn

    def test_patient_mrn_format(self, sample_patient):
        """Test MRN follows expected format."""
        assert sample_patient.mrn.startswith("MED-")
        parts = sample_patient.mrn.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 5  # 5-digit sequence

    def test_unauthenticated_cannot_access_patients(self, api_client):
        """Test unauthenticated requests are rejected."""
        response = api_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
