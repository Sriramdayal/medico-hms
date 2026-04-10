"""
Medico HMS — Core Models
Base models and mixins shared across all apps.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model providing:
    - created_at / updated_at timestamps
    - created_by / updated_by user tracking
    """

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteManager(models.Manager):
    """Manager that filters out soft-deleted records by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(TimestampedModel):
    """
    Abstract model adding soft-delete capability.
    Records are never truly deleted — they are marked with is_deleted=True.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Includes soft-deleted records

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Mark this record as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by", "updated_at"])


class AuditLog(models.Model):
    """
    Immutable audit log for HIPAA compliance.
    Tracks every access and modification to PHI.
    Stored in a dedicated MongoDB collection with TTL index.
    """

    user_id = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=150, blank=True)
    user_role = models.CharField(max_length=50, blank=True)
    action = models.CharField(max_length=20, db_index=True)  # CREATE, READ, UPDATE, DELETE
    resource_type = models.CharField(max_length=100, db_index=True)  # e.g., "Patient", "ProgressNote"
    resource_id = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_id", "-timestamp"]),
            models.Index(fields=["resource_type", "resource_id"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self):
        return f"[{self.timestamp}] {self.username} {self.action} {self.resource_type}:{self.resource_id}"

    @classmethod
    def log(cls, user, action, resource_type, resource_id="", request=None, extra_data=None):
        """Create an audit log entry."""
        return cls.objects.create(
            user_id=str(user.pk) if user and user.is_authenticated else "",
            username=getattr(user, "username", "anonymous"),
            user_role=getattr(getattr(user, "role", None), "name", ""),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            ip_address=cls._get_client_ip(request) if request else None,
            user_agent=request.META.get("HTTP_USER_AGENT", "") if request else "",
            request_method=request.method if request else "",
            request_path=request.path if request else "",
            extra_data=extra_data or {},
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request, accounting for proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
