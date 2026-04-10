"""
Medico HMS — Codes Admin
"""

from django.contrib import admin

from .models import CPTCode, ICD10Code


@admin.register(ICD10Code)
class ICD10CodeAdmin(admin.ModelAdmin):
    list_display = ["code", "description", "category", "is_billable", "version_year"]
    list_filter = ["category", "is_billable", "version_year"]
    search_fields = ["code", "description"]
    list_per_page = 50


@admin.register(CPTCode)
class CPTCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "description", "category", "rvu", "version_year"]
    list_filter = ["category", "version_year"]
    search_fields = ["code", "description"]
    list_per_page = 50
