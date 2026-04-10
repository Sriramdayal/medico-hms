# ===========================================================================
# Medico HMS — Hugging Face Spaces Dockerfile
# ===========================================================================

# ---- Base Stage ----
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies Stage ----
COPY backend/requirements/base.txt /tmp/requirements/base.txt
COPY backend/requirements/prod.txt /tmp/requirements/prod.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements/prod.txt

# ---- Final Stage ----
COPY backend/ /app/

# Create necessary directories and set permissions for HF user (UID 1000)
RUN mkdir -p /app/logs /app/staticfiles /app/media && \
    chmod -R 777 /app/logs /app/staticfiles /app/media

# HF Spaces run as a user with UID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Collect static files (ignore errors if DB is not ready)
RUN DJANGO_SETTINGS_MODULE=medico.settings.prod \
    python manage.py collectstatic --noinput || true

# Hugging Face Spaces expects the app to listen on port 7860
EXPOSE 7860

CMD ["gunicorn", "medico.wsgi:application", \
     "--bind", "0.0.0.0:7860", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
