"""Medico HMS — Results URLs"""
from django.urls import path
from . import views
app_name = "results"
urlpatterns = [
    path("lab/", views.LabResultListCreateView.as_view(), name="lab-result-list"),
    path("lab/<str:pk>/", views.LabResultDetailView.as_view(), name="lab-result-detail"),
    path("imaging/", views.ImagingResultListCreateView.as_view(), name="imaging-result-list"),
    path("imaging/<str:pk>/", views.ImagingResultDetailView.as_view(), name="imaging-result-detail"),
]
