"""
Medico HMS — Accounts Admin Configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Role, StaffProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_clinical", "created_at"]
    list_filter = ["is_clinical"]
    search_fields = ["name"]


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = "Staff Profile"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [StaffProfileInline]
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "department",
        "is_active",
        "is_locked",
    ]
    list_filter = ["role", "department", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name", "employee_id"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Hospital Info",
            {
                "fields": (
                    "role",
                    "department",
                    "employee_id",
                    "license_number",
                )
            },
        ),
        (
            "Security",
            {
                "fields": (
                    "failed_login_attempts",
                    "locked_until",
                    "last_password_change",
                    "password_must_change",
                )
            },
        ),
    )

    def is_locked(self, obj):
        return obj.is_locked

    is_locked.boolean = True
    is_locked.short_description = "Locked?"
