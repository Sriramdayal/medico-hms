"""Medico HMS — Billing Admin"""
from django.contrib import admin
from .models import Charge, Invoice, Payment

class ChargeInline(admin.TabularInline):
    model = Charge
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["patient", "subtotal", "total", "status", "created_at"]
    list_filter = ["status"]
    inlines = [PaymentInline]

@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ["encounter", "charge_type", "description", "total_price", "created_at"]
    list_filter = ["charge_type"]
