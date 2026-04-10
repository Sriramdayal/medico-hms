"""Medico HMS — Pharmacy Admin"""
from django.contrib import admin
from .models import Drug, DrugAdministration, Prescription

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ["name", "generic_name", "form", "strength", "is_controlled", "is_active"]
    list_filter = ["form", "is_controlled", "requires_prescription"]
    search_fields = ["name", "generic_name", "ndc_code"]

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["patient", "drug", "dosage", "frequency", "status", "created_at"]
    list_filter = ["status", "route"]
    search_fields = ["patient__mrn", "drug__name"]

@admin.register(DrugAdministration)
class DrugAdministrationAdmin(admin.ModelAdmin):
    list_display = ["prescription", "administered_by", "administered_at", "dose_given", "was_refused"]
    list_filter = ["was_refused"]
