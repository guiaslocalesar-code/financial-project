# Metricool Publisher - GCP Migration

Este proyecto es la migración del workflow de n8n "Metricool Publisher (Sheets -> Metricool Post y Reels)" hacia una arquitectura nativa en Google Cloud Platform. 

## Arquitectura
- **Cloud Run**: Aplicación Python modular con FastAPI.
- **Cloud Scheduler**: Reemplaza el `Schedule Trigger` de n8n, llamando al endpoint `/run` cada 3 minutos.
- **Secret Manager**: Gestión segura de credenciales (Metricool API, Telegram Bot).
- **Google Sheets**: Fuente de verdad para planificación y marcas.

## Estructura del repositorio
- `app/main.py`: Punto de entrada FastAPI.
- `app/config.py`: Gestión de configuración y secretos.
- `app/services/`: Capa de servicios para integraciones (Sheets, Metricool, Telegram).
- `app/core/`: Lógica de negocio y orquestación del workflow.

## Configuración y Secretos
Los siguientes secretos deben estar definidos en **Secret Manager**:
- `METRICOOL_API_KEY`: Token `X-Mc-Auth`.
- `METRICOOL_USER_ID`: ID numérico del usuario en Metricool.
- `TELEGRAM_BOT_TOKEN`: Token para las notificaciones.
- `TELEGRAM_CHAT_ID_MATIAS`: ID del chat para recibir alertas de error.

**Variables de entorno configurables en Cloud Run:**
- `PLANNING_SHEET_ID`: ID del Google Sheet de planificación.
- `BRANDS_SHEET_ID`: ID del Google Sheet de marcas/manuales.
- `GOOGLE_CLOUD_PROJECT`: ID de tu proyecto en GCP.

## Despliegue en Cloud Run
Ejecuta los siguientes comandos desde la raíz del proyecto:

```bash
# 1. Construir la imagen y subirla a Artifact Registry/GCR
gcloud builds submit --tag gcr.io/TU_PROYECTO/metricool-publisher .

# 2. Desplegar en Cloud Run
# Asegúrate de asignar una cuenta de servicio con permisos para Secret Manager y Google Sheets.
gcloud run deploy metricool-publisher \
  --image gcr.io/TU_PROYECTO/metricool-publisher \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PLANNING_SHEET_ID=1PMvDlydPAJFb_NJo0TgLlHePH0vIZtfS4RK2GVP6bYY,BRANDS_SHEET_ID=1Yt0gJ-BxldHTcgSWXLdY7XPPxs0lmDf5lchJWmMprgA
```

## Configuración de Cloud Scheduler
Crea un job que haga una petición POST/GET al endpoint `/run` de tu servicio Cloud Run con la frecuencia deseada (ej. `*/3 * * * *`).

---
Migrado por **Antigravity - Google Deepmind**
