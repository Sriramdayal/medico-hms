"""
Medico HMS — Test Configuration (conftest.py)
Shared fixtures for all tests.
"""

import pytest
from django.utils import timezone

from apps.accounts.models import CustomUser, Role, StaffProfile


@pytest.fixture
def admin_role(db):
    """Create the ADMIN role."""
    return Role.objects.create(name="ADMIN", description="Administrator", is_clinical=False)


@pytest.fixture
def doctor_role(db):
    """Create the DOCTOR role."""
    return Role.objects.create(name="DOCTOR", description="Doctor", is_clinical=True)


@pytest.fixture
def nurse_role(db):
    """Create the NURSE role."""
    return Role.objects.create(name="NURSE", description="Nurse", is_clinical=True)


@pytest.fixture
def admin_user(db, admin_role):
    """Create an admin user."""
    user = CustomUser.objects.create_user(
        username="admin",
        email="admin@medico.test",
        password="TestPassword123!",
        first_name="Admin",
        last_name="User",
        role=admin_role,
        department="Administration",
    )
    StaffProfile.objects.create(user=user)
    return user


@pytest.fixture
def doctor_user(db, doctor_role):
    """Create a doctor user."""
    user = CustomUser.objects.create_user(
        username="dr.smith",
        email="dr.smith@medico.test",
        password="TestPassword123!",
        first_name="John",
        last_name="Smith",
        role=doctor_role,
        department="Cardiology",
        license_number="MD-12345",
    )
    StaffProfile.objects.create(user=user, specialization="Cardiology", qualification="MD, FACC")
    return user


@pytest.fixture
def nurse_user(db, nurse_role):
    """Create a nurse user."""
    user = CustomUser.objects.create_user(
        username="nurse.jones",
        email="nurse.jones@medico.test",
        password="TestPassword123!",
        first_name="Sarah",
        last_name="Jones",
        role=nurse_role,
        department="Cardiology",
    )
    StaffProfile.objects.create(user=user, qualification="RN, BSN")
    return user


@pytest.fixture
def api_client():
    """Create a DRF test API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Return an API client authenticated as admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authenticated_doctor_client(api_client, doctor_user):
    """Return an API client authenticated as doctor."""
    api_client.force_authenticate(user=doctor_user)
    return api_client


@pytest.fixture
def sample_patient(db, admin_user):
    """Create a sample patient."""
    from apps.patients.models import Patient
    return Patient.objects.create(
        mrn="MED-20260410-00001",
        first_name="Jane",
        last_name="Doe",
        date_of_birth="1990-05-15",
        gender="female",
        blood_type="O+",
        phone="555-0100",
        email="jane.doe@example.com",
        city="New York",
        state="NY",
        created_by=admin_user,
    )


@pytest.fixture
def sample_encounter(db, sample_patient, doctor_user):
    """Create a sample encounter."""
    from apps.clinical.models import Encounter
    return Encounter.objects.create(
        patient=sample_patient,
        attending_doctor=doctor_user,
        encounter_type="outpatient",
        admission_date=timezone.now(),
        chief_complaint="Chest pain and shortness of breath",
        created_by=doctor_user,
    )
