"""Medico HMS — Billing Models (Phase 2)"""
from django.conf import settings
from django.db import models
from apps.core.models import TimestampedModel


class Charge(TimestampedModel):
    CHARGE_TYPE_CHOICES = [
        ("consultation", "Consultation"), ("lab", "Lab Test"),
        ("imaging", "Imaging"), ("drug", "Drug/Medication"),
        ("supply", "Supply"), ("procedure", "Procedure"), ("room", "Room Charges"),
    ]
    encounter = models.ForeignKey("clinical.Encounter", on_delete=models.CASCADE, related_name="charges")
    charge_type = models.CharField(max_length=15, choices=CHARGE_TYPE_CHOICES)
    description = models.CharField(max_length=300)
    cpt_code = models.ForeignKey("codes.CPTCode", null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.charge_type}: {self.description} — ${self.total_price}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Invoice(TimestampedModel):
    STATUS_CHOICES = [
        ("draft", "Draft"), ("finalized", "Finalized"),
        ("partially_paid", "Partially Paid"), ("paid", "Paid"), ("void", "Void"),
    ]
    encounter = models.OneToOneField("clinical.Encounter", on_delete=models.CASCADE, related_name="invoice")
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="invoices")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="draft")
    insurance_claim_id = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice #{self.pk} — {self.patient.mrn} — ${self.total}"

    def calculate_total(self):
        charges = Charge.objects.filter(encounter=self.encounter)
        self.subtotal = sum(c.total_price for c in charges)
        self.total = self.subtotal + self.tax - self.discount
        self.save(update_fields=["subtotal", "total", "updated_at"])


class Payment(TimestampedModel):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"), ("card", "Credit/Debit Card"),
        ("insurance", "Insurance"), ("upi", "UPI"), ("bank_transfer", "Bank Transfer"),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment: ${self.amount} via {self.payment_method}"
