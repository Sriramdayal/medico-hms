"""
Medico HMS — Frontend Template Views
Server-rendered pages for the hospital dashboard.
"""

from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.appointments.models import Appointment
from apps.clinical.models import Allergy, Diagnosis, Encounter, ProgressNote, Vitals
from apps.core.models import AuditLog
from apps.orders.models import ImagingOrder, LabOrder
from apps.patients.models import EmergencyContact, Insurance, Patient
from apps.pharmacy.models import Drug, Prescription


# ===========================================================================
# Authentication
# ===========================================================================


def login_view(request):
    """Login page — POST authenticates and redirects to dashboard."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check lockout
        try:
            user_obj = CustomUser.objects.get(username=username)
            if user_obj.is_locked:
                messages.error(request, "Account is temporarily locked. Please try again later.")
                return render(request, "accounts/login.html", {"form": {"errors": True}})
        except CustomUser.DoesNotExist:
            pass

        user = authenticate(request, username=username, password=password)
        if user is not None:
            user.reset_failed_logins()

            login(request, user)

            AuditLog.log(
                user=user,
                action="LOGIN",
                resource_type="Auth",
                resource_id=str(user.pk),
                request=request,
            )

            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            next_url = request.POST.get("next") or "dashboard"
            return redirect(next_url)
        else:
            # Record failed login
            try:
                user_obj = CustomUser.objects.get(username=username)
                user_obj.record_failed_login()
            except CustomUser.DoesNotExist:
                pass

            return render(request, "accounts/login.html", {"form": {"errors": True}})

    return render(request, "accounts/login.html")


def logout_view(request):
    """Logout and redirect to login."""
    if request.user.is_authenticated:
        AuditLog.log(
            user=request.user,
            action="LOGOUT",
            resource_type="Auth",
            resource_id=str(request.user.pk),
            request=request,
        )
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login-view")


# ===========================================================================
# Dashboard
# ===========================================================================


@login_required(login_url="/login/")
def dashboard_view(request):
    """Main dashboard with stats and recent data."""
    today = timezone.now().date()
    today_start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    today_end = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.max.time())
    )

    stats = {
        "total_patients": Patient.objects.count(),
        "new_patients_today": Patient.objects.filter(created_at__date=today).count(),
        "todays_appointments": Appointment.objects.filter(
            scheduled_start__range=(today_start, today_end)
        ).count(),
        "upcoming_appointments": Appointment.objects.filter(
            scheduled_start__gte=timezone.now(),
            status__in=["scheduled", "confirmed"],
        ).count(),
        "active_encounters": Encounter.objects.filter(status="active").count(),
        "inpatient_count": Encounter.objects.filter(
            status="active", encounter_type="inpatient"
        ).count(),
        "pending_orders": LabOrder.objects.filter(status="pending").count()
        + ImagingOrder.objects.filter(status="pending").count(),
        "stat_orders": LabOrder.objects.filter(priority="stat", status="pending").count(),
        "active_prescriptions": Prescription.objects.filter(status="active").count(),
        "critical_alerts": LabOrder.objects.filter(priority="stat", status="pending").count(),
    }

    recent_patients = Patient.objects.all()[:8]

    todays_appointments = Appointment.objects.filter(
        scheduled_start__range=(today_start, today_end)
    ).select_related("patient")[:10]

    return render(request, "dashboard.html", {
        "active_nav": "dashboard",
        "today": today,
        "stats": stats,
        "recent_patients": recent_patients,
        "todays_appointments": todays_appointments,
    })


# ===========================================================================
# Patients
# ===========================================================================


@login_required(login_url="/login/")
def patient_list_view(request):
    """Patient list with search and create."""
    if request.method == "POST":
        # Create new patient
        patient = Patient(
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
            date_of_birth=request.POST.get("date_of_birth"),
            gender=request.POST.get("gender", "unknown"),
            blood_type=request.POST.get("blood_type", ""),
            phone=request.POST.get("phone", ""),
            email=request.POST.get("email", ""),
            address_line_1=request.POST.get("address_line_1", ""),
            city=request.POST.get("city", ""),
            state=request.POST.get("state", ""),
            postal_code=request.POST.get("postal_code", ""),
            created_by=request.user,
        )
        patient.save()

        AuditLog.log(
            user=request.user,
            action="CREATE",
            resource_type="Patient",
            resource_id=str(patient.pk),
            request=request,
        )

        messages.success(request, f"Patient {patient.full_name} registered — MRN: {patient.mrn}")
        return redirect("patient-detail-view", pk=patient.pk)

    # GET — list patients
    qs = Patient.objects.all()

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(mrn__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )

    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    gender_filter = request.GET.get("gender")
    if gender_filter:
        qs = qs.filter(gender=gender_filter)

    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    patients = paginator.get_page(page)

    return render(request, "patients/patient_list.html", {
        "active_nav": "patients",
        "patients": patients,
        "total_patients": paginator.count,
    })


@login_required(login_url="/login/")
def patient_detail_view(request, pk):
    """Patient detail with all related clinical data."""
    patient = get_object_or_404(Patient, pk=pk)

    AuditLog.log(
        user=request.user,
        action="READ",
        resource_type="Patient",
        resource_id=str(patient.pk),
        request=request,
    )

    return render(request, "patients/patient_detail.html", {
        "active_nav": "patients",
        "patient": patient,
        "encounters": Encounter.objects.filter(patient=patient).select_related("attending_doctor")[:20],
        "encounter_count": Encounter.objects.filter(patient=patient).count(),
        "appointment_count": Appointment.objects.filter(patient=patient).count(),
        "allergies": Allergy.objects.filter(patient=patient),
        "prescriptions": Prescription.objects.filter(patient=patient).select_related("drug")[:20],
        "prescription_count": Prescription.objects.filter(patient=patient).count(),
        "emergency_contacts": EmergencyContact.objects.filter(patient=patient),
        "insurances": Insurance.objects.filter(patient=patient),
    })


# ===========================================================================
# Appointments
# ===========================================================================


@login_required(login_url="/login/")
def appointment_list_view(request):
    """Appointment list with filtering and scheduling."""
    if request.method == "POST":
        appt = Appointment(
            patient_id=request.POST.get("patient"),
            doctor_id=request.POST.get("doctor"),
            appointment_type=request.POST.get("appointment_type", "consultation"),
            scheduled_start=request.POST.get("scheduled_start"),
            scheduled_end=request.POST.get("scheduled_end"),
            reason=request.POST.get("reason", ""),
            created_by=request.user,
        )
        appt.save()
        messages.success(request, "Appointment scheduled successfully!")
        return redirect("appointment-list-view")

    qs = Appointment.objects.select_related("patient", "doctor").all()

    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    type_filter = request.GET.get("type")
    if type_filter:
        qs = qs.filter(appointment_type=type_filter)

    date_filter = request.GET.get("date")
    if date_filter:
        qs = qs.filter(scheduled_start__date=date_filter)

    return render(request, "appointments/appointment_list.html", {
        "active_nav": "appointments",
        "appointments": qs[:50],
        "total_appointments": qs.count(),
        "status_choices": Appointment.STATUS_CHOICES,
        "type_choices": Appointment.TYPE_CHOICES,
        "all_patients": Patient.objects.all()[:100],
        "doctors": CustomUser.objects.filter(role__name="DOCTOR")[:50],
    })


# ===========================================================================
# Clinical Encounters
# ===========================================================================


@login_required(login_url="/login/")
def encounter_list_view(request):
    """Encounter list with search."""
    qs = Encounter.objects.select_related("patient", "attending_doctor").all()

    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    type_filter = request.GET.get("type")
    if type_filter:
        qs = qs.filter(encounter_type=type_filter)

    return render(request, "clinical/encounter_list.html", {
        "active_nav": "encounters",
        "encounters": qs[:50],
        "total_encounters": qs.count(),
    })


@login_required(login_url="/login/")
def encounter_detail_view(request, pk):
    """Encounter detail with notes, vitals, diagnoses, orders."""
    encounter = get_object_or_404(Encounter, pk=pk)

    AuditLog.log(
        user=request.user,
        action="READ",
        resource_type="Encounter",
        resource_id=str(encounter.pk),
        request=request,
    )

    return render(request, "clinical/encounter_detail.html", {
        "active_nav": "encounters",
        "encounter": encounter,
        "notes": ProgressNote.objects.filter(encounter=encounter).select_related("author"),
        "vitals": Vitals.objects.filter(encounter=encounter).select_related("recorded_by"),
        "diagnoses": Diagnosis.objects.filter(encounter=encounter).select_related("icd10_code"),
        "lab_orders": LabOrder.objects.filter(encounter=encounter),
        "imaging_orders": ImagingOrder.objects.filter(encounter=encounter),
    })


# ===========================================================================
# Pharmacy
# ===========================================================================


@login_required(login_url="/login/")
def pharmacy_list_view(request):
    """Pharmacy view with prescriptions and drug directory."""
    return render(request, "pharmacy/pharmacy_list.html", {
        "active_nav": "pharmacy",
        "prescriptions": Prescription.objects.filter(status="active")
            .select_related("drug", "patient", "prescribing_doctor")[:50],
        "drugs": Drug.objects.filter(is_active=True)[:50],
    })


# ===========================================================================
# Audit Log
# ===========================================================================


@login_required(login_url="/login/")
def audit_log_view(request):
    """HIPAA audit trail viewer."""
    return render(request, "audit/audit_log.html", {
        "active_nav": "audit",
        "audit_logs": AuditLog.objects.all()[:100],
    })
