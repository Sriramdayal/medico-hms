"""
Medico HMS — Appointment Models
Scheduling and calendar management.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class Appointment(TimestampedModel):
    """
    Patient appointment with a doctor.
    Follows a state machine: scheduled → checked_in → in_progress → completed
    """

    TYPE_CHOICES = [
        ("consultation", "Consultation"),
        ("follow_up", "Follow-Up"),
        ("procedure", "Procedure"),
        ("emergency", "Emergency"),
        ("lab_visit", "Lab Visit"),
        ("imaging", "Imaging"),
        ("vaccination", "Vaccination"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("no_show", "No Show"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]

    # Valid state transitions
    VALID_TRANSITIONS = {
        "scheduled": ["confirmed", "checked_in", "cancelled", "rescheduled", "no_show"],
        "confirmed": ["checked_in", "cancelled", "rescheduled", "no_show"],
        "checked_in": ["in_progress", "cancelled"],
        "in_progress": ["completed"],
        "completed": [],
        "no_show": ["rescheduled"],
        "cancelled": ["rescheduled"],
        "rescheduled": ["scheduled", "confirmed"],
    }

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
    )
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    scheduled_start = models.DateTimeField(db_index=True)
    scheduled_end = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="scheduled")
    reason = models.TextField(blank=True, help_text="Reason for visit")
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-scheduled_start"]
        indexes = [
            models.Index(fields=["doctor", "scheduled_start"]),
            models.Index(fields=["patient", "-scheduled_start"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Appt: {self.patient.mrn} with Dr. {self.doctor.last_name} @ {self.scheduled_start}"

    def can_transition_to(self, new_status):
        """Check if the appointment can transition to the given status."""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status):
        """Transition appointment to a new status if valid."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'. "
                f"Valid transitions: {self.VALID_TRANSITIONS.get(self.status, [])}"
            )
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])
