"""
Medico HMS — Patient Models
Master Patient Index (MPI) with PHI encryption.
"""

from django.db import models

from apps.core.encryption import EncryptedCharField, EncryptedEmailField, EncryptedTextField
from apps.core.models import SoftDeleteModel, TimestampedModel


class Patient(SoftDeleteModel):
    """
    Master Patient Index (MPI).
    Core patient demographics with PHI fields encrypted at the application level.
    """

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("unknown", "Unknown"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("deceased", "Deceased"),
    ]

    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    # MRN auto-generated via signal
    mrn = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Medical Record Number",
    )

    # Encrypted PHI fields
    first_name = EncryptedCharField(max_length=500)
    last_name = EncryptedCharField(max_length=500)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True)

    # Highly sensitive identifiers
    ssn = EncryptedCharField(max_length=500, blank=True, verbose_name="SSN/National ID")
    email = EncryptedEmailField(max_length=500, blank=True)
    phone = EncryptedCharField(max_length=500, blank=True)
    address_line_1 = EncryptedTextField(blank=True)
    address_line_2 = EncryptedCharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="US", blank=True)

    # Medical info
    marital_status = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=50, default="English")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["mrn"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.mrn} — {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )


class EmergencyContact(TimestampedModel):
    """Emergency contact linked to a patient."""

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50)
    phone = EncryptedCharField(max_length=500)
    email = EncryptedEmailField(max_length=500, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return f"{self.name} ({self.relationship}) for {self.patient.mrn}"


class Insurance(TimestampedModel):
    """Patient insurance information."""

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="insurances"
    )
    provider_name = models.CharField(max_length=200)
    policy_number = EncryptedCharField(max_length=500)
    group_number = models.CharField(max_length=50, blank=True)
    plan_type = models.CharField(max_length=50, blank=True)  # HMO, PPO, etc.
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    subscriber_name = models.CharField(max_length=200, blank=True)
    subscriber_relationship = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["-is_primary", "-effective_date"]
        verbose_name_plural = "Insurance records"

    def __str__(self):
        return f"{self.provider_name} — {self.patient.mrn}"

    @property
    def is_active(self):
        from datetime import date
        today = date.today()
        if self.expiry_date:
            return self.effective_date <= today <= self.expiry_date
        return self.effective_date <= today
