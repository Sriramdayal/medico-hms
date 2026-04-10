"""Medico HMS — Orders Views"""
from rest_framework import generics, permissions
from .models import ImagingOrder, LabOrder
from .serializers import ImagingOrderSerializer, LabOrderSerializer


class LabOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = LabOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "priority", "encounter"]

    def get_queryset(self):
        return LabOrder.objects.select_related("ordering_doctor").all()

    def perform_create(self, serializer):
        serializer.save(ordering_doctor=self.request.user, created_by=self.request.user)


class LabOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = LabOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LabOrder.objects.all()


class ImagingOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = ImagingOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "priority", "modality", "encounter"]

    def get_queryset(self):
        return ImagingOrder.objects.select_related("ordering_doctor").all()

    def perform_create(self, serializer):
        serializer.save(ordering_doctor=self.request.user, created_by=self.request.user)


class ImagingOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ImagingOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImagingOrder.objects.all()
