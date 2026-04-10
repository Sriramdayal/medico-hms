"""
Medico HMS — Patient Signals
Auto-generates unique MRN (Medical Record Number) on patient creation.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Patient


@receiver(pre_save, sender=Patient)
def generate_mrn(sender, instance, **kwargs):
    """
    Generate a unique MRN before saving a new patient.
    Format: MED-YYYYMMDD-XXXXX (e.g., MED-20260410-00001)
    """
    if not instance.mrn:
        today = timezone.now().strftime("%Y%m%d")
        prefix = f"MED-{today}-"

        # Find the latest MRN for today
        latest = (
            Patient.all_objects.filter(mrn__startswith=prefix)
            .order_by("-mrn")
            .first()
        )

        if latest:
            last_seq = int(latest.mrn.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        instance.mrn = f"{prefix}{new_seq:05d}"
