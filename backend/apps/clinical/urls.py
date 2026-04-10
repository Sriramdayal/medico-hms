"""Medico HMS — Clinical URLs"""
from django.urls import path
from . import views

app_name = "clinical"

urlpatterns = [
    # Encounters
    path("encounters/", views.EncounterListCreateView.as_view(), name="encounter-list"),
    path("encounters/<str:pk>/", views.EncounterDetailView.as_view(), name="encounter-detail"),

    # Nested under encounters
    path("encounters/<str:encounter_id>/diagnoses/", views.DiagnosisListCreateView.as_view(), name="diagnosis-list"),
    path("encounters/<str:encounter_id>/notes/", views.ProgressNoteListCreateView.as_view(), name="note-list"),
    path("encounters/<str:encounter_id>/vitals/", views.VitalsListCreateView.as_view(), name="vitals-list"),

    # Notes detail
    path("notes/<str:pk>/", views.ProgressNoteDetailView.as_view(), name="note-detail"),

    # Allergies (nested under patient in patients app, but also accessible here)
    path("patients/<str:patient_id>/allergies/", views.AllergyListCreateView.as_view(), name="allergy-list"),
]
