"""
Medico HMS — Patient Admin
"""

from django.contrib import admin

from .models import EmergencyContact, Insurance, Patient


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


class InsuranceInline(admin.TabularInline):
    model = Insurance
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["mrn", "first_name", "last_name", "date_of_birth", "gender", "status"]
    list_filter = ["status", "gender", "blood_type"]
    search_fields = ["mrn", "first_name", "last_name"]
    inlines = [EmergencyContactInline, InsuranceInline]
    readonly_fields = ["mrn", "created_at", "updated_at"]
