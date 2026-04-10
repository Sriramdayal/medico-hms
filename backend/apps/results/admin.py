"""Medico HMS — Results Admin"""
from django.contrib import admin
from .models import ImagingResult, LabResult

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ["order", "performed_by", "interpretation", "is_critical", "created_at"]
    list_filter = ["is_critical", "interpretation"]

@admin.register(ImagingResult)
class ImagingResultAdmin(admin.ModelAdmin):
    list_display = ["order", "radiologist", "created_at"]
