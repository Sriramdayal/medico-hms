"""Medico HMS — Appointment Admin"""
from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "appointment_type", "scheduled_start", "status"]
    list_filter = ["status", "appointment_type"]
    search_fields = ["patient__mrn", "doctor__username", "reason"]
    date_hierarchy = "scheduled_start"
