"""
ASGI config for Medico HMS project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medico.settings.prod")

application = get_asgi_application()
