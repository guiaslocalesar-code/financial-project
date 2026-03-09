# Análisis del workflow: Metricool Publisher

## Descripción del workflow original
El flujo original en n8n automatiza la publicación de contenidos en redes sociales utilizando Google Sheets como base de datos y Metricool como plataforma de programación. 

- **Trigger**: Se dispara cada 3 minutos mediante un nodo `Schedule Trigger`.
- **Servicios involucrados**: Google Sheets (dos documentos distintos), Metricool API, Telegram API y OpenAI (como validador auxiliar).
- **Lógica**: Lee una hoja de planificación, filtra posts pendientes con fecha futura, busca el ID de Metricool del cliente en otra hoja, normaliza las URLs de medios (especialmente de Google Drive) y finalmente agenda el post en Metricool.

## Malas prácticas detectadas
- **Secretos Hardcodeados**: La API Key de Metricool (`X-Mc-Auth`) y el `userId` están presentes directamente en el código JavaScript de varios nodos. Esto es un riesgo de seguridad crítico.
- **Identificadores de Infraestructura Fijos**: Los IDs de las hojas de cálculo de Google están hardcodeados en los nodos, lo que dificulta la portabilidad o el cambio de documentos sin editar el workflow.
- **Complejidad en Nodos de Código**: Gran parte de la lógica de transformación y validación de fechas está escrita en JavaScript dentro de bloques de código de n8n, lo que hace que sea difícil de testear y versionar.
- **Gestión de Errores Frágil**: Aunque existen ramas de error, la lógica de reintento o reporte depende de nodos dispersos, lo que puede llevar a estados inconsistentes si el workflow falla a mitad de una ejecución por lotes.
- **Cálculo Manual de Timezone**: Se realiza un cálculo manual de `argentinaTime` con offsets fijos (`-180` minutos), lo cual no contempla cambios por horario de verano o variaciones en el entorno de ejecución.

## Cambios propuestos y mejoras
- **Uso de Secret Manager**: Todos los tokens (Metricool, Telegram) se almacenarán en Google Cloud Secret Manager. Nunca estarán en el código.
- **Arquitectura Modular en Python**: Se implementará una estructura de servicios (`google_sheets_service.py`, `metricool_service.py`) que separa la lógica de negocio de los detalles de implementación de las APIs.
- **Containerización con Cloud Run**: El código correrá en un contenedor administrado, permitiendo un manejo de dependencias (`requirements.txt`) mucho más robusto que los nodos de n8n.
- **Logging Centralizado**: Uso de `google-cloud-logging` para que cada paso del proceso (filtrado, normalización, publicación) sea trazable y alertable en GCP.
- **Manejo de Fechas con `pytz`**: Uso de librerías estándar de Python para manejar la zona horaria de Argentina de forma precisa y segura.

## Impacto en el comportamiento
- **Consistencia**: El comportamiento funcional será idéntico: se leerán las mismas columnas y se enviará la misma información a Metricool.
- **Mejora en Normalización**: Se optimizará la detección de URLs de Google Drive para asegurar que Metricool siempre reciba un enlace directo compatible.
- **Notificaciones**: Se mantendrán las alertas de Telegram, pero configuradas de forma centralizada.

## Requisitos de configuración
### Secretos (Secret Manager)
- `METRICOOL_API_KEY`: Token `X-Mc-Auth`.
- `METRICOOL_USER_ID`: ID numérico del usuario en Metricool.
- `TELEGRAM_BOT_TOKEN`: Token del bot para notificaciones.
- `TELEGRAM_CHAT_ID_MATIAS`: ID del chat de destino.

### Variables de Entorno / Config
- `PLANNING_SHEET_ID`: `1PMvDlydPAJFb_NJo0TgLlHePH0vIZtfS4RK2GVP6bYY`
- `BRANDS_SHEET_ID`: `1Yt0gJ-BxldHTcgSWXLdY7XPPxs0lmDf5lchJWmMprgA`
- `GOOGLE_APPLICATION_CREDENTIALS`: Ruta al Service Account con permisos de lectura/escritura en Sheets.
