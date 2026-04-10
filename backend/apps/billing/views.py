"""Medico HMS — Billing Views"""
from rest_framework import generics, permissions
from .models import Charge, Invoice, Payment
from .serializers import ChargeSerializer, InvoiceSerializer, PaymentSerializer

class ChargeListCreateView(generics.ListCreateAPIView):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["encounter", "charge_type"]

class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "patient"]

class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Payment.objects.filter(invoice_id=self.kwargs.get("invoice_id"))
    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user, created_by=self.request.user)
