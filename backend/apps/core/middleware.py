"""
Medico HMS — Audit Logging Middleware
Logs all API requests that access PHI endpoints.
"""

import logging
import time

from apps.core.models import AuditLog

logger = logging.getLogger("apps.core.middleware")

# Endpoints that access PHI and require audit logging
PHI_ENDPOINTS = [
    "/api/v1/patients/",
    "/api/v1/clinical/",
    "/api/v1/pharmacy/",
    "/api/v1/orders/",
    "/api/v1/results/",
    "/api/v1/billing/",
]


class AuditLogMiddleware:
    """
    Middleware that creates audit log entries for all requests
    touching PHI-related endpoints (HIPAA requirement).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record start time
        start_time = time.time()

        # Process the request
        response = self.get_response(request)

        # Only log authenticated requests to PHI endpoints
        if self._should_log(request):
            try:
                duration_ms = int((time.time() - start_time) * 1000)
                action = self._determine_action(request.method)

                AuditLog.log(
                    user=request.user,
                    action=action,
                    resource_type=self._extract_resource_type(request.path),
                    resource_id=self._extract_resource_id(request.path),
                    request=request,
                    extra_data={
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                    },
                )
            except Exception:
                # Never let audit logging crash the request
                logger.exception("Failed to create audit log entry")

        return response

    def _should_log(self, request):
        """Check if this request should be audit-logged."""
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return False

        return any(request.path.startswith(prefix) for prefix in PHI_ENDPOINTS)

    @staticmethod
    def _determine_action(method):
        """Map HTTP method to audit action."""
        method_map = {
            "GET": "READ",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        return method_map.get(method, "OTHER")

    @staticmethod
    def _extract_resource_type(path):
        """Extract the resource type from the URL path."""
        parts = path.strip("/").split("/")
        # /api/v1/patients/ -> "patients"
        if len(parts) >= 3:
            return parts[2].title()
        return "Unknown"

    @staticmethod
    def _extract_resource_id(path):
        """Extract the resource ID from the URL path if present."""
        parts = path.strip("/").split("/")
        # /api/v1/patients/{id}/ -> id
        if len(parts) >= 4:
            return parts[3]
        return ""
