# 🗂️ Index Finanzas: Guías Locales AR

Este documento centraliza el estado actual del proyecto, su arquitectura, conexiones y flujos de despliegue.

---

## 🚀 Resumen del Proyecto
El **Agente Financiero** es una plataforma integral para la gestión contable y financiera de agencias de marketing digital. Permite controlar empresas, clientes, servicios, presupuestos, facturación electrónica (AFIP), cobros, gastos y liquidación de comisiones.

---

## 🏗️ Arquitectura del Sistema

### 🖥️ Frontend (React / Next.js)
Ubicación: `agente-financiero-guias-frontend/`

- **Framework**: Next.js 14.2 (App Router).
- **Estilos**: Tailwind CSS con componentes Premium (Glassmorphism, Lucide Icons, Framer Motion).
- **Estado/Datos**: TanStack Query (React Query) para caché y sincronización.
- **Conexiones API**: Centralizadas en `src/services/api.ts` mediante Axios.
  - **Auth API**: Nodo.js (Externo) para gestión de usuarios y marcas.
  - **Finance API**: FastAPI (Backend propio) para lógica de negocio.

### ⚙️ Backend (Python / FastAPI)
Ubicación: `agente-financiero-guias-backend/`

- **Framework**: FastAPI (Asíncrono).
- **ORM**: SQLAlchemy 2.0 (Async).
- **Base de Datos**: PostgreSQL alojado en **Supabase**.
- **Integraciones**: 
  - **AFIP**: Módulo `pyafipws` para facturación electrónica.
- **Módulos Core**:
  - `clients`: Gestión de clientes comerciales.
  - `services`: Catálogo de servicios por empresa.
  - `transactions`: Movimientos (Ingresos/Egresos).
  - `budgets (Income/Expense)`: Presupuestos mensuales.
  - `invoices`: Facturación y generación de PDFs (ReportLab).
  - `commissions`: Liquidación de comisiones a terceros.

---

## 🔗 Conexiones y Bases de Datos

### Base de Datos Principal
- **Motor**: PostgreSQL 17.
- **Conexión**: Se utiliza una URL de conexión asíncrona (`postgresql+asyncpg://...`) definida en las variables de entorno de Cloud Run.
- **Esquema**: Definido mediante modelos de SQLAlchemy en `app/models/`.

### Conexión Frontend -> Backend
El frontend se conecta al backend a través de un proxy configurado en Vercel o directamente al dominio de Cloud Run:
- **Production URL**: `https://agente-financiero-backend-815637135726.us-east1.run.app`
- **Internal Prefix**: `/finance-api` (mapeado a `/api/v1` en el backend).

---

## 📦 Despliegue y CI/CD

### Backend (Google Cloud Run)
Se utiliza **GitHub Actions** para el despliegue continuo:
1. **Trigger**: Push a la rama `main` afectando la carpeta `agente-financiero-guias-backend/`.
2. **Build**: Docker build del contenedor usando el `Dockerfile` (incluye librerías de sistema para AFIP).
3. **Registry**: Google Artifact Registry.
4. **Deploy**: Google Cloud Run (us-east1).
5. **Secrets**: Las variables `DATABASE_URL`, `SUPABASE_KEY` y `AFIP_KEYS` se inyectan desde GitHub Secrets.

### Frontend (Vercel)
Despliegue automático al hacer push a `main`:
1. **Build**: `next build`.
2. **Environment**: `NEXT_PUBLIC_API_URL` configurada en el panel de Vercel.

---

## 📑 Índice de Documentación Relevante

| Documento | Descripción |
| :--- | :--- |
| [README.md](file:///c:/Users/lea32/Finanzas-Guias/README.md) | Guía rápida de inicio y estructura de carpetas. |
| [BACKEND README](file:///c:/Users/lea32/Finanzas-Guias/agente-financiero-guias-backend/README.md) | Documentación técnica de la API y modelos. |
| [FRONTEND README](file:///c:/Users/lea32/Finanzas-Guias/agente-financiero-guias-frontend/README.md) | Guía de desarrollo UI y componentes. |
| [AFIP INTEGRATION](file:///c:/Users/lea32/Finanzas-Guias/agente-financiero-guias-backend/afip_integration/README.md) | Detalles del módulo de facturación electrónica. |

---

## 🛠️ Historial de Ajustes Recientes (Rescate de Producción)
1. **Normalización de Rutas**: Eliminación de `trailing slashes` para evitar errores 404.
2. **Flexibilidad Auth**: Eliminación de dependencias de JWT obligatorias en rutas de lectura.
3. **Tipos de Datos**: Cambio de `UUID` a `str` en esquemas Pydantic para soportar IDs de base de datos legados.
4. **Estabilidad Invoices**: Adición de dependencias `swig`, `libssl` y `reportlab` para restaurar PDF y AFIP.
5. **Case Normalization**: Cambio de Enums a MAYÚSCULAS para coincidir con los filtros del portal.

---
*Documentación generada por Antigravity - Advanced Agentic Coding.*
