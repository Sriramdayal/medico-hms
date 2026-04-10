"""
Medico HMS — Production Settings
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if h.strip()
]
# Render sets RENDER_EXTERNAL_HOSTNAME automatically
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)

# --------------------------------------------------------------------------
# Security hardening
# --------------------------------------------------------------------------

# Render terminates SSL at the proxy — tell Django to trust X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if h and not h.startswith(".")
]

# --------------------------------------------------------------------------
# Static files — WhiteNoise (already in MIDDLEWARE from base.py)
# --------------------------------------------------------------------------

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------------------------------
# Remove browsable API in production
# --------------------------------------------------------------------------

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
)

# --------------------------------------------------------------------------
# Logging — console only (Render captures stdout)
# --------------------------------------------------------------------------

LOGGING["handlers"].pop("file", None)  # noqa: F405
for _logger in LOGGING.get("loggers", {}).values():  # noqa: F405
    if "file" in _logger.get("handlers", []):
        _logger["handlers"].remove("file")
