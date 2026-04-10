"""
Medico HMS — Clinical Models
Electronic Health Record: Encounters, Progress Notes, Vitals, Allergies, Diagnoses.
"""

from django.conf import settings
from django.db import models

from apps.core.encryption import EncryptedTextField
from apps.core.models import TimestampedModel


class Encounter(TimestampedModel):
    """
    A single clinical visit/interaction between a patient and provider.
    Central entity linking notes, orders, prescriptions, and billing.
    """

    TYPE_CHOICES = [
        ("inpatient", "Inpatient"),
        ("outpatient", "Outpatient"),
        ("emergency", "Emergency"),
        ("observation", "Observation"),
        ("telehealth", "Telehealth"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("discharged", "Discharged"),
        ("transferred", "Transferred"),
        ("cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="encounters"
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encounter",
    )
    attending_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attended_encounters",
    )
    encounter_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")
    chief_complaint = models.TextField()
    discharge_summary = EncryptedTextField(blank=True)
    discharge_disposition = models.CharField(max_length=100, blank=True)

    # ML risk score (populated by Phase 3 analytics)
    readmission_risk_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-admission_date"]
        indexes = [
            models.Index(fields=["patient", "-admission_date"]),
            models.Index(fields=["attending_doctor", "-admission_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Encounter: {self.patient.mrn} ({self.encounter_type}) — {self.status}"

    @property
    def length_of_stay(self):
        """Calculate length of stay in days."""
        if self.discharge_date and self.admission_date:
            delta = self.discharge_date - self.admission_date
            return delta.days
        return None


class Diagnosis(TimestampedModel):
    """
    Links an ICD-10 code to an encounter.
    M2M through model for Encounter ↔ ICD10Code.
    """

    TYPE_CHOICES = [
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("admitting", "Admitting"),
        ("working", "Working"),
    ]

    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="diagnoses"
    )
    icd10_code = models.ForeignKey(
        "codes.ICD10Code", on_delete=models.PROTECT, related_name="diagnoses"
    )
    diagnosis_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="primary")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["diagnosis_type", "-created_at"]
        verbose_name_plural = "Diagnoses"

    def __str__(self):
        return f"{self.icd10_code.code} ({self.diagnosis_type}) — {self.encounter.patient.mrn}"


class ProgressNote(TimestampedModel):
    """
    SOAP-format clinical note linked to an encounter.
    All SOAP fields are encrypted as they contain PHI.
    """

    NOTE_TYPE_CHOICES = [
        ("progress", "Progress Note"),
        ("admission", "Admission Note"),
        ("discharge", "Discharge Note"),
        ("consultation", "Consultation Note"),
        ("procedure", "Procedure Note"),
        ("nursing", "Nursing Note"),
    ]

    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="progress_notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="authored_notes",
    )
    note_type = models.CharField(max_length=15, choices=NOTE_TYPE_CHOICES)

    # SOAP fields — all encrypted
    subjective = EncryptedTextField(blank=True, help_text="Patient's reported symptoms")
    objective = EncryptedTextField(blank=True, help_text="Clinical findings and observations")
    assessment = EncryptedTextField(blank=True, help_text="Clinical assessment and diagnosis")
    plan = EncryptedTextField(blank=True, help_text="Treatment plan")

    # Signing
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["encounter", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.note_type} by {self.author.get_full_name()} — {self.encounter.patient.mrn}"


class Vitals(TimestampedModel):
    """
    Vital signs recorded during an encounter.
    """

    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="vitals"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_vitals",
    )

    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, help_text="°F"
    )
    heart_rate = models.IntegerField(null=True, blank=True, help_text="bpm")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, help_text="mmHg")
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, help_text="mmHg")
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="breaths/min")
    oxygen_saturation = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, help_text="%"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, help_text="kg"
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, help_text="cm"
    )
    pain_level = models.IntegerField(
        null=True, blank=True, help_text="Pain scale 0-10"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Vitals"

    def __str__(self):
        return f"Vitals @ {self.created_at} — {self.encounter.patient.mrn}"

    @property
    def bmi(self):
        """Calculate BMI from weight (kg) and height (cm)."""
        if self.weight and self.height and self.height > 0:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    @property
    def blood_pressure(self):
        """Formatted blood pressure string."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None


class Allergy(TimestampedModel):
    """
    Patient allergy record.
    Linked to patient (not encounter) since allergies persist across visits.
    """

    SEVERITY_CHOICES = [
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
        ("life_threatening", "Life Threatening"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("resolved", "Resolved"),
    ]

    ALLERGY_TYPE_CHOICES = [
        ("drug", "Drug"),
        ("food", "Food"),
        ("environmental", "Environmental"),
        ("other", "Other"),
    ]

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="allergies"
    )
    allergen = models.CharField(max_length=200)
    allergy_type = models.CharField(max_length=15, choices=ALLERGY_TYPE_CHOICES, default="drug")
    reaction = models.TextField(help_text="Description of allergic reaction")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    onset_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_allergies",
    )

    class Meta:
        ordering = ["-severity", "allergen"]
        verbose_name_plural = "Allergies"

    def __str__(self):
        return f"{self.allergen} ({self.severity}) — {self.patient.mrn}"
