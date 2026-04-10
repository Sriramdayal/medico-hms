"""Medico HMS — Inventory URLs"""
from django.urls import path
from . import views
app_name = "inventory"
urlpatterns = [
    path("items/", views.InventoryItemListCreateView.as_view(), name="item-list"),
    path("items/<str:pk>/", views.InventoryItemDetailView.as_view(), name="item-detail"),
    path("transactions/", views.StockTransactionListCreateView.as_view(), name="transaction-list"),
]
