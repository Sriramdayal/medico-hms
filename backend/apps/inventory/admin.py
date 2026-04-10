"""Medico HMS — Inventory Admin"""
from django.contrib import admin
from .models import InventoryItem, StockTransaction

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["name", "item_type", "sku", "quantity_on_hand", "reorder_level", "location", "is_low_stock"]
    list_filter = ["item_type", "location"]
    search_fields = ["name", "sku"]

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ["item", "transaction_type", "quantity", "performed_by", "created_at"]
    list_filter = ["transaction_type"]
