# 🏥 Medico — Hospital Management System

> A comprehensive, HIPAA-aware Hospital Management System built with **Django 5.2**, **Django REST Framework**, and **MongoDB**.

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **MongoDB 7+** (standalone or replica set)
- **Redis 7+** (for Celery)
- **Docker** (recommended for MongoDB + Redis)

### Option 1: Docker (Recommended)

```bash
# Clone and start all services
git clone <repo-url> && cd medico
cp .env.example .env
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Seed medical codes (ICD-10, CPT)
docker compose exec web python manage.py import_medical_codes --seed

# Access the app
# API:      http://localhost:8000/api/docs/
# Admin:    http://localhost:8000/admin/
```

### Option 2: Local Development

```bash
# 1. Install dependencies
cd backend
pip install -r requirements/dev.txt

# 2. Start MongoDB (replica set required for transactions)
mongod --replSet rs0 --dbpath ./data/db
# In another terminal:
mongosh --eval "rs.initiate()"

# 3. Start Redis
redis-server

# 4. Configure environment
cp ../.env.example ../.env
# Edit .env with your MongoDB URI

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Seed medical codes
python manage.py import_medical_codes --seed

# 8. Run the server
python manage.py runserver
```

## 📋 API Documentation

Once running, access the interactive API docs at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🏗️ Architecture

```
Modular Monolith (Django 5.2 + DRF + MongoDB)
├── apps/accounts/     — Authentication, RBAC, JWT
├── apps/patients/     — Master Patient Index (MPI)
├── apps/appointments/ — Scheduling, Calendar
├── apps/clinical/     — EHR (Encounters, Notes, Vitals, Allergies)
├── apps/pharmacy/     — Drugs, Prescriptions, MAR
├── apps/orders/       — Lab & Imaging Orders
├── apps/results/      — Lab & Imaging Results
├── apps/inventory/    — Supply & Drug Inventory
├── apps/billing/      — Charges, Invoices, Payments
├── apps/codes/        — ICD-10, CPT Reference Data
├── apps/analytics/    — ML & Reporting (Phase 3)
└── apps/core/         — Base models, Audit, Encryption, Permissions
```

## 🔐 Security Features

- **Field-level encryption** for all PHI (names, SSN, DOB, phone, notes)
- **Argon2** password hashing (HIPAA best practice)
- **JWT authentication** with 15-min access / 24-hr refresh token rotation
- **RBAC** with roles: Doctor, Nurse, Admin, Billing, Pharmacist, Lab Tech, Radiologist
- **Audit logging** for all PHI access (user, IP, action, timestamp)
- **Account lockout** after 5 failed login attempts
- **Session auto-logout** after 15 minutes of inactivity

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest --cov=apps --cov-report=term-missing -v

# Run specific test module
pytest tests/test_accounts/ -v
pytest tests/test_patients/ -v
```

## 📦 Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Django 5.2 + DRF 3.17 |
| Database | MongoDB 7 (django-mongodb-backend) |
| Cache/Broker | Redis 7 |
| Task Queue | Celery 5.x |
| Auth | JWT (SimpleJWT) |
| Encryption | Fernet (cryptography) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 📄 License

Private — All rights reserved.
