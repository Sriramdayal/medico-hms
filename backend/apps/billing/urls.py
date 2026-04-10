"""Medico HMS — Billing URLs"""
from django.urls import path
from . import views
app_name = "billing"
urlpatterns = [
    path("charges/", views.ChargeListCreateView.as_view(), name="charge-list"),
    path("invoices/", views.InvoiceListCreateView.as_view(), name="invoice-list"),
    path("invoices/<str:pk>/", views.InvoiceDetailView.as_view(), name="invoice-detail"),
    path("invoices/<str:invoice_id>/payments/", views.PaymentListCreateView.as_view(), name="payment-list"),
]
