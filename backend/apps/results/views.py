"""Medico HMS — Results Views"""
from rest_framework import generics, permissions
from .models import ImagingResult, LabResult
from .serializers import ImagingResultSerializer, LabResultSerializer

class LabResultListCreateView(generics.ListCreateAPIView):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class LabResultDetailView(generics.RetrieveUpdateAPIView):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class ImagingResultListCreateView(generics.ListCreateAPIView):
    queryset = ImagingResult.objects.all()
    serializer_class = ImagingResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class ImagingResultDetailView(generics.RetrieveUpdateAPIView):
    queryset = ImagingResult.objects.all()
    serializer_class = ImagingResultSerializer
    permission_classes = [permissions.IsAuthenticated]
