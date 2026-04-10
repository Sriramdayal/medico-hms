"""Medico HMS — Appointment Views"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentStatusSerializer,
)


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/appointments/      — List appointments
    POST /api/v1/appointments/      — Book an appointment
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "appointment_type", "doctor", "patient"]
    search_fields = ["reason", "notes"]
    ordering_fields = ["scheduled_start", "created_at"]

    def get_queryset(self):
        qs = Appointment.objects.select_related("patient", "doctor").all()
        # Filter by date range if provided
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            qs = qs.filter(scheduled_start__gte=start_date)
        if end_date:
            qs = qs.filter(scheduled_start__lte=end_date)
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/appointments/{id}/
    PATCH /api/v1/appointments/{id}/
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.select_related("patient", "doctor").all()


class AppointmentStatusUpdateView(APIView):
    """
    PATCH /api/v1/appointments/{id}/status/
    Update appointment status following valid state transitions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        try:
            appointment.transition_to(new_status)
            if new_status == "cancelled":
                appointment.cancellation_reason = serializer.validated_data.get(
                    "cancellation_reason", ""
                )
                appointment.save(update_fields=["cancellation_reason"])

            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
