"""
Medico HMS — Custom DRF Permissions
Role-based access control for the hospital management system.
"""

from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    """Allow access only to users with the DOCTOR role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "DOCTOR"
        )


class IsNurse(BasePermission):
    """Allow access only to users with the NURSE role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "NURSE"
        )


class IsAdmin(BasePermission):
    """Allow access only to users with the ADMIN role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "ADMIN"
        )


class IsBillingStaff(BasePermission):
    """Allow access only to users with the BILLING role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "BILLING"
        )


class IsPharmacist(BasePermission):
    """Allow access only to users with the PHARMACIST role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "PHARMACIST"
        )


class IsLabTech(BasePermission):
    """Allow access only to users with the LAB_TECH role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "LAB_TECH"
        )


class IsClinicalStaff(BasePermission):
    """Allow access to doctors, nurses, or lab techs."""

    CLINICAL_ROLES = {"DOCTOR", "NURSE", "LAB_TECH", "RADIOLOGIST", "PHARMACIST"}

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name in self.CLINICAL_ROLES
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Full access for ADMIN users; read-only for everyone else.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return (
            hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == "ADMIN"
        )
