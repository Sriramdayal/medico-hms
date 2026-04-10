# ===========================================================================
# Medico HMS — Docker Multi-Stage Build
# ===========================================================================

# ---- Base Stage ----
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies Stage ----
FROM base AS dependencies

COPY backend/requirements/base.txt /tmp/requirements/base.txt
COPY backend/requirements/prod.txt /tmp/requirements/prod.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements/prod.txt

# ---- Development Stage ----
FROM base AS development

COPY backend/requirements/base.txt /tmp/requirements/base.txt
COPY backend/requirements/dev.txt /tmp/requirements/dev.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements/dev.txt

COPY backend/ /app/

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ---- Production Stage ----
FROM dependencies AS production

COPY backend/ /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media /var/log/medico

# Collect static files
RUN DJANGO_SETTINGS_MODULE=medico.settings.prod \
    MONGODB_URI=mongodb://localhost:27017/medico \
    python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "medico.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
