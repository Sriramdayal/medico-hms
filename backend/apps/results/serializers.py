"""Medico HMS — Results Serializers"""
from rest_framework import serializers
from .models import ImagingResult, LabResult

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

class ImagingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagingResult
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
