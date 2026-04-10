"""
Medico HMS — Accounts Views
Authentication and user management API endpoints.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.models import AuditLog
from apps.core.permissions import IsAdmin

from .models import CustomUser
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Authenticate user and return JWT token pair.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        tokens = serializer.validated_data["tokens"]

        # Audit log
        AuditLog.log(
            user=user,
            action="LOGIN",
            resource_type="Auth",
            resource_id=str(user.pk),
            request=request,
        )

        return Response(
            {
                "tokens": tokens,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklist the refresh token to log out.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            AuditLog.log(
                user=request.user,
                action="LOGOUT",
                resource_type="Auth",
                resource_id=str(request.user.pk),
                request=request,
            )

            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TokenRefreshCustomView(TokenRefreshView):
    """
    POST /api/v1/auth/refresh/
    Refresh the access token using a valid refresh token.
    Uses rotate + blacklist for security.
    """

    pass


class CurrentUserView(APIView):
    """
    GET /api/v1/auth/me/
    Return the current authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Change the current user's password.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.last_password_change = timezone.now()
        user.password_must_change = False
        user.save(update_fields=["password", "last_password_change", "password_must_change"])

        AuditLog.log(
            user=user,
            action="UPDATE",
            resource_type="Auth",
            resource_id=str(user.pk),
            request=request,
            extra_data={"detail": "Password changed"},
        )

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/users/ — List all users (admin only)
    POST /api/v1/users/ — Create a new user (admin only)
    """

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.select_related("role").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/users/{id}/ — Retrieve user details (admin only)
    PATCH /api/v1/users/{id}/ — Update user details (admin only)
    """

    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.select_related("role").all()
