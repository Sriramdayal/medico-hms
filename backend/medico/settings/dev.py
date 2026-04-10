"""
Medico HMS — Development Settings
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Development CORS — allow all
CORS_ALLOW_ALL_ORIGINS = True

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405

# --------------------------------------------------------------------------
# Database — Use SQLite for local dev if PostgreSQL is not available
# Set DB_ENGINE=postgresql in .env to use PostgreSQL instead
# --------------------------------------------------------------------------
import os

_db_engine = os.environ.get("DB_ENGINE", "sqlite3")

if _db_engine == "postgresql":
    # Use PostgreSQL from base.py
    pass
else:
    # SQLite fallback — zero-config for local development
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Logging — more verbose in development
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

# Create logs directory
os.makedirs(BASE_DIR / "logs", exist_ok=True)  # noqa: F405

