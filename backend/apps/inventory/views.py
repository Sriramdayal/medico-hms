"""Medico HMS — Inventory Views"""
from rest_framework import generics, permissions
from .models import InventoryItem, StockTransaction
from .serializers import InventoryItemSerializer, StockTransactionSerializer

class InventoryItemListCreateView(generics.ListCreateAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "sku"]
    filterset_fields = ["item_type", "location"]

class InventoryItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class StockTransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = StockTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = StockTransaction.objects.all()
        item_id = self.request.query_params.get("item")
        if item_id:
            qs = qs.filter(item_id=item_id)
        return qs

    def perform_create(self, serializer):
        txn = serializer.save(performed_by=self.request.user, created_by=self.request.user)
        # Update inventory quantity
        item = txn.item
        item.quantity_on_hand += txn.quantity
        item.save(update_fields=["quantity_on_hand", "updated_at"])
