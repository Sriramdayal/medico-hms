"""Medico HMS — Orders Admin"""
from django.contrib import admin
from .models import ImagingOrder, LabOrder

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ["encounter", "ordering_doctor", "priority", "status", "specimen_type", "created_at"]
    list_filter = ["status", "priority"]

@admin.register(ImagingOrder)
class ImagingOrderAdmin(admin.ModelAdmin):
    list_display = ["encounter", "ordering_doctor", "modality", "body_part", "priority", "status", "created_at"]
    list_filter = ["status", "priority", "modality"]
