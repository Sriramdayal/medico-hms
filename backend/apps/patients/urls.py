"""
Medico HMS — Patient URL Configuration
"""

from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.PatientListCreateView.as_view(), name="patient-list"),
    path("<str:pk>/", views.PatientDetailView.as_view(), name="patient-detail"),
    path("mrn/<str:mrn>/", views.PatientByMRNView.as_view(), name="patient-by-mrn"),
    path(
        "<str:patient_id>/emergency-contacts/",
        views.EmergencyContactListCreateView.as_view(),
        name="emergency-contact-list",
    ),
    path(
        "<str:patient_id>/insurance/",
        views.InsuranceListCreateView.as_view(),
        name="insurance-list",
    ),
]
