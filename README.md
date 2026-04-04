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
