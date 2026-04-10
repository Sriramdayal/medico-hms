"""Medico HMS — Inventory Models (Phase 2)"""
from django.conf import settings
from django.db import models
from apps.core.models import TimestampedModel

class InventoryItem(TimestampedModel):
    ITEM_TYPE_CHOICES = [("drug", "Drug"), ("supply", "Supply"), ("equipment", "Equipment")]
    name = models.CharField(max_length=200)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    drug = models.ForeignKey("pharmacy.Drug", null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_items")
    sku = models.CharField(max_length=50, unique=True)
    quantity_on_hand = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100, help_text="warehouse, pharmacy, ward-A")

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["sku"])]

    def __str__(self):
        return f"{self.name} ({self.quantity_on_hand} on hand)"

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level


class StockTransaction(TimestampedModel):
    TXN_TYPE_CHOICES = [
        ("received", "Received"), ("dispensed", "Dispensed"),
        ("adjusted", "Adjusted"), ("returned", "Returned"), ("expired", "Expired"),
    ]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TXN_TYPE_CHOICES)
    quantity = models.IntegerField(help_text="Positive for in, negative for out")
    reference_encounter = models.ForeignKey("clinical.Encounter", null=True, blank=True, on_delete=models.SET_NULL)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} × {self.item.name}"
