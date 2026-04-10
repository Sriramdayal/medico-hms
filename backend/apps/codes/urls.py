"""
Medico HMS — Codes URL Configuration
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "codes"

urlpatterns = [
    path("icd10/", views.ICD10CodeListView.as_view(), name="icd10-list"),
    path("icd10/<str:pk>/", views.ICD10CodeDetailView.as_view(), name="icd10-detail"),
    path("cpt/", views.CPTCodeListView.as_view(), name="cpt-list"),
    path("cpt/<str:pk>/", views.CPTCodeDetailView.as_view(), name="cpt-detail"),
]
