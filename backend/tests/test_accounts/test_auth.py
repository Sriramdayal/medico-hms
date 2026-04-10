"""
Medico HMS — Accounts Tests
Tests for authentication, authorization, and user management.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthentication:
    """Tests for login, logout, and token flow."""

    def test_login_success(self, api_client, doctor_user):
        """Test successful login returns JWT tokens and user data."""
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "dr.smith", "password": "TestPassword123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert response.data["user"]["username"] == "dr.smith"

    def test_login_invalid_credentials(self, api_client, doctor_user):
        """Test login with invalid credentials returns 400."""
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "dr.smith", "password": "WrongPassword!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_account_lockout(self, api_client, doctor_user):
        """Test account lockout after too many failed attempts."""
        for _ in range(5):
            api_client.post(
                "/api/v1/auth/login/",
                {"username": "dr.smith", "password": "WrongPassword!"},
                format="json",
            )

        # Next attempt should report lockout
        response = api_client.post(
            "/api/v1/auth/login/",
            {"username": "dr.smith", "password": "TestPassword123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_current_user(self, authenticated_doctor_client):
        """Test GET /api/v1/auth/me/ returns current user."""
        response = authenticated_doctor_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "dr.smith"

    def test_unauthenticated_access_denied(self, api_client):
        """Test unauthenticated requests are rejected."""
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserManagement:
    """Tests for admin user management."""

    def test_admin_can_list_users(self, authenticated_admin_client, doctor_user):
        """Test admin can list all users."""
        response = authenticated_admin_client.get("/api/v1/auth/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_doctor_cannot_list_users(self, authenticated_doctor_client):
        """Test non-admin users cannot list all users."""
        response = authenticated_doctor_client.get("/api/v1/auth/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
