# Guía de Despliegue en Google Cloud Run

Para desplegar tu backend en Google Cloud Run de forma automatizada y gratuita, sigue estos pasos:

## 1. Preparar Google Cloud (GCP)
Ejecuta estos comandos en tu terminal (con el SDK de Google Cloud instalado) o en el Cloud Shell de Google:

```bash
# Habilitar servicios necesarios
gcloud services enable run.googleapis.com \
                       containerregistry.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com

# Crear el repositorio para la imagen (si no existe)
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=us-east1
```

## 2. Configurar Secretos en GitHub
Ve a tu repositorio en GitHub > **Settings** > **Secrets and variables** > **Actions** y agrega los siguientes "Repository secrets":

| Secreto | Descripción |
|---|---|
| `GCP_PROJECT_ID` | El ID de tu proyecto de Google Cloud. |
| `GCP_SA_KEY` | El contenido del archivo JSON de una Service Account con permisos de "Cloud Run Admin" y "Storage Admin". |
| `DATABASE_URL` | Tu URL de Supabase Pooler. |
| `SUPABASE_URL` | `https://fumejzkghviszmyfjegg.supabase.co` |
| `SUPABASE_KEY` | Tu Service Role Key de Supabase. |
| `SECRET_KEY` | Tu clave secreta del backend. |
| `ENCRYPTION_KEY` | Tu clave de encriptación del backend. |
| `ALLOWED_ORIGINS` | `*` o el dominio de tu frontend. |

## 3. Despliegue Automático
Cada vez que hagas un `git push` a la rama `main`, GitHub Actions construirá la imagen y la desplegará en Cloud Run automáticamente.

---
*Si prefieres hacerlo manualmente la primera vez, el comando es:*
```bash
gcloud run deploy agente-financiero-backend \
    --source ./agente-financiero-guias-backend \
    --region us-east1 \
    --allow-unauthenticated
```
