"""
Medico HMS — Custom Exception Handler
Standardized API error responses.
"""

import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

logger = logging.getLogger("apps.core.exceptions")


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps all errors in a consistent format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": { ... }
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "error": {
                "code": _get_error_code(exc),
                "message": _get_error_message(exc, response),
                "details": response.data if isinstance(response.data, dict) else {"detail": response.data},
            }
        }
        response.data = error_data

    return response


def _get_error_code(exc):
    """Get a machine-readable error code from the exception."""
    if hasattr(exc, "default_code"):
        return exc.default_code.upper()
    return type(exc).__name__.upper()


def _get_error_message(exc, response):
    """Get a human-readable error message."""
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else "An error occurred"
    return str(exc)


class AccountLocked(APIException):
    """Raised when a user account is locked due to too many failed login attempts."""

    status_code = status.HTTP_423_LOCKED
    default_detail = "Account is temporarily locked due to multiple failed login attempts. Please try again later."
    default_code = "account_locked"


class InsufficientPermissions(APIException):
    """Raised when a user doesn't have the required role/permission."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have the required permissions to perform this action."
    default_code = "insufficient_permissions"
