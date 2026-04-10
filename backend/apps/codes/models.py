"""
Medico HMS — Medical Reference Code Models
ICD-10 diagnosis codes and CPT procedure codes.
"""

from django.db import models


class ICD10Code(models.Model):
    """
    International Classification of Diseases, 10th Revision.
    Used for diagnosis coding.
    """

    code = models.CharField(max_length=10, unique=True, db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=200, blank=True)
    chapter = models.CharField(max_length=200, blank=True)
    is_billable = models.BooleanField(default=True)
    version_year = models.IntegerField(default=2026)

    class Meta:
        ordering = ["code"]
        verbose_name = "ICD-10 Code"
        verbose_name_plural = "ICD-10 Codes"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.description[:80]}"


class CPTCode(models.Model):
    """
    Current Procedural Terminology codes.
    Used for procedure and service billing.
    """

    code = models.CharField(max_length=5, unique=True, db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=200, blank=True)
    subcategory = models.CharField(max_length=200, blank=True)
    rvu = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Relative Value Unit",
    )
    version_year = models.IntegerField(default=2026)

    class Meta:
        ordering = ["code"]
        verbose_name = "CPT Code"
        verbose_name_plural = "CPT Codes"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.description[:80]}"
