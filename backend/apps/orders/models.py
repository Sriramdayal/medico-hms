"""
Medico HMS — Orders Models (Phase 2)
Clinical ordering — Lab and Imaging orders.
Separate collections (no multi-table inheritance in MongoDB).
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel

PRIORITY_CHOICES = [
    ("stat", "STAT"), ("urgent", "Urgent"), ("routine", "Routine"),
]

ORDER_STATUS_CHOICES = [
    ("pending", "Pending"), ("accepted", "Accepted"),
    ("in_progress", "In Progress"), ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

MODALITY_CHOICES = [
    ("xray", "X-Ray"), ("ct", "CT Scan"), ("mri", "MRI"),
    ("ultrasound", "Ultrasound"), ("pet", "PET Scan"),
    ("mammography", "Mammography"), ("fluoroscopy", "Fluoroscopy"),
]


class LabOrder(TimestampedModel):
    """Lab-specific clinical order."""

    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.CASCADE, related_name="lab_orders")
    ordering_doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lab_orders")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="routine")
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default="pending")
    cpt_code = models.ForeignKey("codes.CPTCode", null=True, blank=True, on_delete=models.SET_NULL)
    clinical_notes = models.TextField(blank=True)
    specimen_type = models.CharField(max_length=50, blank=True, help_text="blood, urine, tissue")
    fasting_required = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self):
        return f"Lab Order: {self.encounter.patient.mrn} — {self.status}"


class ImagingOrder(TimestampedModel):
    """Imaging-specific clinical order."""

    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.CASCADE, related_name="imaging_orders")
    ordering_doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="imaging_orders")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="routine")
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default="pending")
    cpt_code = models.ForeignKey("codes.CPTCode", null=True, blank=True, on_delete=models.SET_NULL)
    clinical_notes = models.TextField(blank=True)
    body_part = models.CharField(max_length=100)
    modality = models.CharField(max_length=15, choices=MODALITY_CHOICES)
    contrast = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self):
        return f"Imaging Order: {self.modality} {self.body_part} — {self.encounter.patient.mrn}"
