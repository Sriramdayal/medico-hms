"""Medico HMS — Billing Serializers"""
from rest_framework import serializers
from .models import Charge, Invoice, Payment

class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = "__all__"
        read_only_fields = ["id", "total_price", "created_at"]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

class InvoiceSerializer(serializers.ModelSerializer):
    charges = ChargeSerializer(source="encounter.charges", many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
