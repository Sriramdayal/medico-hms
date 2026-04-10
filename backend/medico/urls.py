"""
Medico HMS — URL Configuration
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.frontend import views as frontend_views

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ==========================================
    # Frontend (Django template views)
    # ==========================================
    path("", frontend_views.dashboard_view, name="dashboard"),
    path("login/", frontend_views.login_view, name="login-view"),
    path("logout/", frontend_views.logout_view, name="logout-view"),

    # Patients
    path("patients/", frontend_views.patient_list_view, name="patient-list-view"),
    path("patients/<str:pk>/", frontend_views.patient_detail_view, name="patient-detail-view"),

    # Appointments
    path("appointments/", frontend_views.appointment_list_view, name="appointment-list-view"),

    # Clinical
    path("encounters/", frontend_views.encounter_list_view, name="encounter-list-view"),
    path("encounters/<str:pk>/", frontend_views.encounter_detail_view, name="encounter-detail-view"),

    # Pharmacy
    path("pharmacy/", frontend_views.pharmacy_list_view, name="pharmacy-list-view"),

    # Audit
    path("audit/", frontend_views.audit_log_view, name="audit-log-view"),

    # ==========================================
    # API v1 (DRF endpoints)
    # ==========================================
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/patients/", include("apps.patients.urls")),
    path("api/v1/appointments/", include("apps.appointments.urls")),
    path("api/v1/clinical/", include("apps.clinical.urls")),
    path("api/v1/pharmacy/", include("apps.pharmacy.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/results/", include("apps.results.urls")),
    path("api/v1/inventory/", include("apps.inventory.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/codes/", include("apps.codes.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),

    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = "Medico HMS Administration"
admin.site.site_title = "Medico HMS"
admin.site.index_title = "Hospital Management System"
