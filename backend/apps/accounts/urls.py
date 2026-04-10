"""
Medico HMS — Accounts URL Configuration
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("refresh/", views.TokenRefreshCustomView.as_view(), name="token-refresh"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),

    # User management (admin)
    path("users/", views.UserListCreateView.as_view(), name="user-list"),
    path("users/<str:pk>/", views.UserDetailView.as_view(), name="user-detail"),
]
