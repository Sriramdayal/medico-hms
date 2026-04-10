"""
Medico HMS — Codes Serializers
"""

from rest_framework import serializers

from .models import CPTCode, ICD10Code


class ICD10CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICD10Code
        fields = ["id", "code", "description", "category", "chapter", "is_billable", "version_year"]


class CPTCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPTCode
        fields = ["id", "code", "description", "category", "subcategory", "rvu", "version_year"]
