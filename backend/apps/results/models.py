"""Medico HMS — Results Models (Phase 2)"""
from django.conf import settings
from django.db import models
from apps.core.encryption import EncryptedTextField
from apps.core.models import TimestampedModel


class LabResult(TimestampedModel):
    order = models.OneToOneField("orders.LabOrder", on_delete=models.CASCADE, related_name="result")
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="performed_labs")
    result_data = models.JSONField(help_text='Structured results, e.g., {"WBC": 7.5, "RBC": 4.8}')
    units = models.JSONField(null=True, blank=True)
    reference_ranges = models.JSONField(null=True, blank=True)
    interpretation = models.CharField(max_length=20, blank=True, help_text="normal, abnormal, critical")
    is_critical = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="verified_labs")
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Lab Result for Order #{self.order_id}"


class ImagingResult(TimestampedModel):
    order = models.OneToOneField("orders.ImagingOrder", on_delete=models.CASCADE, related_name="result")
    radiologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="imaging_reads")
    findings = EncryptedTextField()
    impression = EncryptedTextField()
    report_file = models.FileField(upload_to="imaging_reports/", blank=True)

    def __str__(self):
        return f"Imaging Result for Order #{self.order_id}"
