"""Medico HMS — Orders URLs"""
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("lab/", views.LabOrderListCreateView.as_view(), name="lab-order-list"),
    path("lab/<str:pk>/", views.LabOrderDetailView.as_view(), name="lab-order-detail"),
    path("imaging/", views.ImagingOrderListCreateView.as_view(), name="imaging-order-list"),
    path("imaging/<str:pk>/", views.ImagingOrderDetailView.as_view(), name="imaging-order-detail"),
]
