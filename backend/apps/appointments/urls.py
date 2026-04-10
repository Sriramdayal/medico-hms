"""Medico HMS — Appointment URLs"""
from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.AppointmentListCreateView.as_view(), name="appointment-list"),
    path("<str:pk>/", views.AppointmentDetailView.as_view(), name="appointment-detail"),
    path("<str:pk>/status/", views.AppointmentStatusUpdateView.as_view(), name="appointment-status"),
]
