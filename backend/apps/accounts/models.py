"""
Medico HMS — Accounts Models
Custom user model with RBAC for hospital staff.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.core.encryption import EncryptedCharField


class Role(models.Model):
    """
    System roles for RBAC.
    Predefined roles: DOCTOR, NURSE, ADMIN, BILLING, PHARMACIST, LAB_TECH, RADIOLOGIST
    """

    ROLE_CHOICES = [
        ("DOCTOR", "Doctor"),
        ("NURSE", "Nurse"),
        ("ADMIN", "Administrator"),
        ("BILLING", "Billing Staff"),
        ("PHARMACIST", "Pharmacist"),
        ("LAB_TECH", "Lab Technician"),
        ("RADIOLOGIST", "Radiologist"),
        ("RECEPTIONIST", "Receptionist"),
    ]

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    is_clinical = models.BooleanField(
        default=False,
        help_text="Whether this role has access to clinical data",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Represents all hospital staff members.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )
    department = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Medical license number (for clinical staff)",
    )
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Security fields
    last_password_change = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    password_must_change = models.BooleanField(default=False)

    class Meta:
        ordering = ["username"]
        indexes = [
            models.Index(fields=["employee_id"]),
        ]

    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        return f"{self.get_full_name()} ({role_name})"

    @property
    def is_locked(self):
        """Check if the account is currently locked."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def record_failed_login(self):
        """Record a failed login attempt and lock account if threshold exceeded."""
        from django.conf import settings

        self.failed_login_attempts += 1
        if self.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_THRESHOLD:
            self.locked_until = timezone.now() + timezone.timedelta(
                seconds=settings.ACCOUNT_LOCKOUT_DURATION
            )
        self.save(update_fields=["failed_login_attempts", "locked_until"])

    def reset_failed_logins(self):
        """Reset failed login counter after successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=["failed_login_attempts", "locked_until"])


class StaffProfile(models.Model):
    """
    Extended profile for hospital staff with clinical details.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    specialization = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    phone = EncryptedCharField(max_length=500, blank=True)  # PHI — encrypted
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="staff_avatars/", blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the staff member is currently available for assignments",
    )

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"
