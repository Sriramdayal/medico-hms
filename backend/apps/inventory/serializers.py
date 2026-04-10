"""Medico HMS — Inventory Serializers"""
from rest_framework import serializers
from .models import InventoryItem, StockTransaction

class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    class Meta:
        model = InventoryItem
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

class StockTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransaction
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
