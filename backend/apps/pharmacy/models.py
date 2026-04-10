"""
Medico HMS — Pharmacy Models
Drug reference, prescriptions, and medication administration records (MAR).
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class Drug(TimestampedModel):
    """Drug reference table."""

    FORM_CHOICES = [
        ("tablet", "Tablet"), ("capsule", "Capsule"),
        ("injection", "Injection"), ("syrup", "Syrup"),
        ("cream", "Cream"), ("ointment", "Ointment"),
        ("drops", "Drops"), ("inhaler", "Inhaler"),
        ("patch", "Patch"), ("suppository", "Suppository"),
        ("iv_fluid", "IV Fluid"), ("other", "Other"),
    ]

    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    ndc_code = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="NDC Code")
    drug_class = models.CharField(max_length=100, blank=True)
    form = models.CharField(max_length=15, choices=FORM_CHOICES)
    strength = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=200, blank=True)
    requires_prescription = models.BooleanField(default=True)
    is_controlled = models.BooleanField(default=False, help_text="Controlled substance (DEA scheduled)")
    contraindications = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["ndc_code"]),
            models.Index(fields=["generic_name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.strength} {self.form})"


class Prescription(TimestampedModel):
    """Prescription linking a drug to a patient encounter."""

    ROUTE_CHOICES = [
        ("oral", "Oral"), ("iv", "Intravenous"), ("im", "Intramuscular"),
        ("sc", "Subcutaneous"), ("topical", "Topical"), ("inhaled", "Inhaled"),
        ("rectal", "Rectal"), ("sublingual", "Sublingual"), ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"), ("dispensed", "Dispensed"),
        ("completed", "Completed"), ("discontinued", "Discontinued"),
        ("on_hold", "On Hold"),
    ]

    encounter = models.ForeignKey(
        "clinical.Encounter", on_delete=models.CASCADE, related_name="prescriptions"
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="prescriptions"
    )
    prescribing_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prescriptions"
    )
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT, related_name="prescriptions")
    dosage = models.CharField(max_length=100, help_text='e.g., "500mg"')
    frequency = models.CharField(max_length=100, help_text='e.g., "TID (three times daily)"')
    route = models.CharField(max_length=15, choices=ROUTE_CHOICES)
    duration_days = models.IntegerField()
    quantity = models.IntegerField()
    refills_allowed = models.IntegerField(default=0)
    instructions = models.TextField(blank=True, help_text="Special instructions for patient")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")
    discontinued_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Rx: {self.drug.name} for {self.patient.mrn}"


class DrugAdministration(TimestampedModel):
    """Records each time a drug is given to a patient (MAR entry)."""

    ROUTE_CHOICES = Prescription.ROUTE_CHOICES

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="administrations"
    )
    administered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="administered_drugs"
    )
    administered_at = models.DateTimeField()
    dose_given = models.CharField(max_length=100)
    route = models.CharField(max_length=15, choices=ROUTE_CHOICES)
    site = models.CharField(max_length=100, blank=True, help_text='e.g., "left deltoid"')
    notes = models.TextField(blank=True)
    patient_response = models.TextField(blank=True, help_text="Patient's response to medication")
    was_refused = models.BooleanField(default=False)
    refusal_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-administered_at"]

    def __str__(self):
        return f"Admin: {self.prescription.drug.name} @ {self.administered_at}"
