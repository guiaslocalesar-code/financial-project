<<<<<<< HEAD
# Marketing Agency Financial Backend

Scalable financial engine for marketing agencies. Built with FastAPI, PostgreSQL (Cloud SQL), and SQLAlchemy 2.0.

## 🚀 Stack
- **Python**: 3.12+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15 (GCP Cloud SQL)
- **Migrations**: Alembic
- **AFIP Integration**: `pyafipws` (WSFE)

## 📁 Repository Structure
- `app/main.py`: Entry point.
- `app/models/`: Database models (sqlalchemy).
- `app/schemas/`: Validation and response models (pydantic).
- `app/routers/`: API endpoints.
- `app/services/`: Business logic (AFIP, budgets, dashboard).
- `alembic/`: Database migration history.

## 🔗 API Contract (v1)

### Base URL: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/companies/` | Create a new company root entity. |
| POST | `/clients/` | Create a client (validates CUIT/DNI). |
| POST | `/invoices/` | Create an invoice draft. |
| POST | `/invoices/{id}/emit` | Emit invoice in AFIP and get CAE. |
| GET | `/dashboard/summary` | Get income, expenses, and balance. |
| GET | `/dashboard/profitability` | Profitability analysis per service. |
| POST | `/budgets/{id}/pay` | Pay a budget and create a transaction. |

## 🛠️ Setup Local
1. Clone the repository.
2. `pip install -r requirements.txt`
3. Configure `.env` (use `.env.example` as base).
4. `python -m alembic upgrade head`
5. `uvicorn app.main:app --reload`

## ☁️ Deployment
This project is ready for **Railway**.
The `alembic.ini` and `env.py` are configured for async connections to Cloud SQL.
CORS is configured via `ALLOWED_ORIGINS` env var.
=======
# Agente Financiero - Guías Locales AR

Sistema de gestión financiera para agencias de marketing digital. Incluye backend (FastAPI + PostgreSQL) y frontend (React/Next.js).

## Estructura del Repositorio

```
├── agente-financiero-guias-backend/   # API Backend (FastAPI)
├── agente-financiero-guias-frontend/  # Frontend (React)
└── .github/workflows/                # CI/CD (Cloud Run)
```

## Backend

- **FastAPI** con SQLAlchemy async
- **PostgreSQL** (Supabase)
- Facturación electrónica AFIP
- Gestión de presupuestos, transacciones, comisiones y deudas
- Autenticación JWT

## Despliegue

El backend se deploya automáticamente a **Google Cloud Run** cuando se hace push a `main` con cambios en `agente-financiero-guias-backend/`.

---
Desarrollado por **ATG - Antigravity**
>>>>>>> financial-project/main
