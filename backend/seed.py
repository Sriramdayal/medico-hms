"""
Medico HMS — Seed script for demo data.
Run: python manage.py shell < seed.py
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medico.settings.dev")

import django
django.setup()

from datetime import date, timedelta
from django.utils import timezone

from apps.accounts.models import CustomUser, Role, StaffProfile
from apps.appointments.models import Appointment
from apps.clinical.models import Allergy, Encounter
from apps.codes.models import CPTCode, ICD10Code
from apps.patients.models import Patient
from apps.pharmacy.models import Drug

admin = CustomUser.objects.get(username="admin")

# Roles
dr_role, _ = Role.objects.get_or_create(name="DOCTOR", defaults={"description": "Doctor", "is_clinical": True})
nurse_role, _ = Role.objects.get_or_create(name="NURSE", defaults={"description": "Nurse", "is_clinical": True})
Role.objects.get_or_create(name="PHARMACIST", defaults={"description": "Pharmacist", "is_clinical": True})
Role.objects.get_or_create(name="BILLING", defaults={"description": "Billing Staff", "is_clinical": False})

# Doctor
if not CustomUser.objects.filter(username="dr.sharma").exists():
    doc = CustomUser.objects.create_user(
        username="dr.sharma", password="Doctor@123456!", email="dr.sharma@medico.local",
        first_name="Rajesh", last_name="Sharma", role=dr_role,
        department="Cardiology", license_number="MD-54321",
    )
    StaffProfile.objects.create(user=doc, specialization="Cardiology", qualification="MD, DM Cardiology")
    print("Created doctor: dr.sharma")
else:
    doc = CustomUser.objects.get(username="dr.sharma")

# Nurse
if not CustomUser.objects.filter(username="nurse.priya").exists():
    nurse = CustomUser.objects.create_user(
        username="nurse.priya", password="Nurse@123456!", email="nurse.priya@medico.local",
        first_name="Priya", last_name="Patel", role=nurse_role, department="Cardiology",
    )
    StaffProfile.objects.create(user=nurse)
    print("Created nurse: nurse.priya")

# Patients
patients_data = [
    ("Amit", "Kumar", date(1985, 3, 15), "male", "A+", "555-0101", "amit@example.com"),
    ("Sneha", "Reddy", date(1992, 7, 22), "female", "O+", "555-0102", "sneha@example.com"),
    ("Ravi", "Singh", date(1978, 11, 5), "male", "B+", "555-0103", "ravi@example.com"),
    ("Anita", "Desai", date(1965, 1, 30), "female", "AB-", "555-0104", "anita@example.com"),
    ("Vikram", "Joshi", date(2001, 6, 18), "male", "O-", "555-0105", "vikram@example.com"),
]

patients = []
for i, (fn, ln, dob, g, bt, ph, em) in enumerate(patients_data, 1):
    p, created = Patient.objects.get_or_create(
        mrn=f"MED-20260410-{i:05d}",
        defaults=dict(
            first_name=fn, last_name=ln, date_of_birth=dob, gender=g,
            blood_type=bt, phone=ph, email=em, city="Hyderabad", state="Telangana",
            created_by=admin,
        ),
    )
    patients.append(p)
    if created:
        print(f"Created patient: {fn} {ln}")

# Allergies
if Allergy.objects.count() == 0:
    Allergy.objects.create(patient=patients[0], allergen="Penicillin", allergy_type="drug", reaction="Rash and hives", severity="moderate", status="active", reported_by=doc)
    Allergy.objects.create(patient=patients[1], allergen="Peanuts", allergy_type="food", reaction="Anaphylaxis", severity="severe", status="active", reported_by=doc)
    Allergy.objects.create(patient=patients[2], allergen="Dust Mites", allergy_type="environmental", reaction="Sneezing, runny nose", severity="mild", status="active", reported_by=doc)
    print("Created allergies")

# ICD-10 codes
icd_data = [
    ("I10", "Essential Hypertension", "I"),
    ("I25.10", "Coronary Artery Disease", "I"),
    ("E11.9", "Type 2 Diabetes Mellitus", "E"),
    ("J18.9", "Pneumonia, unspecified", "J"),
    ("M54.5", "Low Back Pain", "M"),
    ("J06.9", "Acute Upper Respiratory Infection", "J"),
    ("K21.0", "GERD with esophagitis", "K"),
]
for code, desc, cat in icd_data:
    ICD10Code.objects.get_or_create(code=code, defaults={"description": desc, "category": cat})
print(f"ICD-10 codes: {ICD10Code.objects.count()}")

# CPT codes
cpt_data = [
    ("99213", "Office Visit Level 3", "E&M"),
    ("99214", "Office Visit Level 4", "E&M"),
    ("93000", "Electrocardiogram", "Cardiology"),
    ("71046", "Chest X-Ray 2 Views", "Radiology"),
    ("80053", "Comprehensive Metabolic Panel", "Lab"),
]
for code, desc, cat in cpt_data:
    CPTCode.objects.get_or_create(code=code, defaults={"description": desc, "category": cat})
print(f"CPT codes: {CPTCode.objects.count()}")

# Drugs
drug_data = [
    ("Amoxicillin", "Amoxicillin", "NDC-001", "capsule", "500mg", "Antibiotic"),
    ("Metformin", "Metformin HCl", "NDC-002", "tablet", "500mg", "Antidiabetic"),
    ("Amlodipine", "Amlodipine Besylate", "NDC-003", "tablet", "5mg", "Antihypertensive"),
    ("Atorvastatin", "Atorvastatin Calcium", "NDC-004", "tablet", "20mg", "Statin"),
    ("Omeprazole", "Omeprazole", "NDC-005", "capsule", "20mg", "PPI"),
]
for name, generic, ndc, form, strength, drug_class in drug_data:
    Drug.objects.get_or_create(ndc_code=ndc, defaults={"name": name, "generic_name": generic, "form": form, "strength": strength, "drug_class": drug_class})
print(f"Drugs: {Drug.objects.count()}")

# Encounters
now = timezone.now()
if Encounter.objects.count() == 0:
    Encounter.objects.create(patient=patients[0], attending_doctor=doc, encounter_type="outpatient", admission_date=now, chief_complaint="Chest pain and shortness of breath on exertion", created_by=doc)
    Encounter.objects.create(patient=patients[1], attending_doctor=doc, encounter_type="emergency", admission_date=now - timedelta(hours=3), chief_complaint="Severe headache and dizziness for 2 hours", created_by=doc)
    Encounter.objects.create(patient=patients[2], attending_doctor=doc, encounter_type="inpatient", admission_date=now - timedelta(days=1), chief_complaint="Persistent fever and cough for 5 days", created_by=doc)
    print("Created encounters")

# Appointments
if Appointment.objects.count() == 0:
    for i, p in enumerate(patients[:4]):
        Appointment.objects.create(
            patient=p, doctor=doc, appointment_type="consultation",
            scheduled_start=now + timedelta(hours=i + 1),
            scheduled_end=now + timedelta(hours=i + 1, minutes=30),
            reason="Follow-up visit", created_by=admin,
        )
    print("Created appointments")

print(f"\n=== Seed Complete ===")
print(f"Patients: {Patient.objects.count()}")
print(f"Encounters: {Encounter.objects.count()}")
print(f"Appointments: {Appointment.objects.count()}")
print(f"Drugs: {Drug.objects.count()}")
print(f"ICD-10: {ICD10Code.objects.count()}")
print(f"CPT: {CPTCode.objects.count()}")
