"""
Medico HMS — Accounts Serializers
"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Role, StaffProfile


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description", "is_clinical"]


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = [
            "specialization",
            "qualification",
            "phone",
            "bio",
            "date_of_joining",
            "is_available",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user detail/list views."""

    role = RoleSerializer(read_only=True)
    profile = StaffProfileSerializer(read_only=True)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "department",
            "employee_id",
            "license_number",
            "is_active",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users (admin only)."""

    password = serializers.CharField(write_only=True, min_length=12)
    role_id = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role_id",
            "department",
            "employee_id",
            "license_number",
        ]

    def create(self, validated_data):
        role_id = validated_data.pop("role_id")
        password = validated_data.pop("password")

        role = Role.objects.get(pk=role_id)
        user = CustomUser(**validated_data)
        user.role = role
        user.set_password(password)
        user.save()

        # Create staff profile
        StaffProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # Check if account is locked
        try:
            user = CustomUser.objects.get(username=username)
            if user.is_locked:
                raise serializers.ValidationError(
                    "Account is temporarily locked due to multiple failed login attempts."
                )
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        # Authenticate
        user = authenticate(username=username, password=password)
        if not user:
            # Record failed attempt
            try:
                user_obj = CustomUser.objects.get(username=username)
                user_obj.record_failed_login()
            except CustomUser.DoesNotExist:
                pass
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")

        # Reset failed login counter on success
        user.reset_failed_logins()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=12)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
