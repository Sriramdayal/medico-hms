"""Medico HMS — Analytics Views (Phase 3 placeholder)"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class AnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({"message": "Analytics module — Phase 3 (coming soon)", "status": "placeholder"})
