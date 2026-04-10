"""Medico HMS — Pharmacy URLs"""
from django.urls import path
from . import views

app_name = "pharmacy"

urlpatterns = [
    path("drugs/", views.DrugListCreateView.as_view(), name="drug-list"),
    path("drugs/<str:pk>/", views.DrugDetailView.as_view(), name="drug-detail"),
    path("prescriptions/", views.PrescriptionListCreateView.as_view(), name="prescription-list"),
    path("prescriptions/<str:pk>/", views.PrescriptionDetailView.as_view(), name="prescription-detail"),
    path("prescriptions/<str:prescription_id>/administrations/", views.DrugAdministrationListCreateView.as_view(), name="administration-list"),
]
