"""Medico HMS — Clinical Admin"""
from django.contrib import admin
from .models import Allergy, Diagnosis, Encounter, ProgressNote, Vitals


class DiagnosisInline(admin.TabularInline):
    model = Diagnosis
    extra = 0

class ProgressNoteInline(admin.StackedInline):
    model = ProgressNote
    extra = 0

class VitalsInline(admin.TabularInline):
    model = Vitals
    extra = 0

@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ["patient", "attending_doctor", "encounter_type", "admission_date", "status"]
    list_filter = ["status", "encounter_type"]
    search_fields = ["patient__mrn", "chief_complaint"]
    inlines = [DiagnosisInline, ProgressNoteInline, VitalsInline]

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ["patient", "allergen", "severity", "allergy_type", "status"]
    list_filter = ["severity", "allergy_type", "status"]
    search_fields = ["allergen", "patient__mrn"]
