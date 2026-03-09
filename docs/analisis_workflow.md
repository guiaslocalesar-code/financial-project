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

## Workflow 2: Historias (n8n → GCP)

### Descripción del workflow original de Historias
Este segundo flujo de n8n ("Metricool Publisher (Sheets -> Metricool STORYS) - MultiMarca [Fixed]") está diseñado específicamente para publicar Historias. Lee desde el mismo documento base pero apunta a la hoja `planificacion_historia`.

### Diferencias respecto al flujo de Posts/Reels
La lógica de extracción, validación de fechas futuras, filtro por redes activas, búsqueda del ID de la marca y normalización de URLs (incluso de Google Drive) es estructuralmente **idéntica** al flujo de Posts. 

La única diferencia real radica en el payload enviado en la petición HTTP POST a la API de Metricool:
- Se inyecta `instagramData: { type: 'STORY', autoPublish: true }`
- Se inyecta `facebookData: { type: 'STORY' }`

### Malas prácticas adicionales detectadas
Las mismas que en el flujo principal: secretos fijos (`X-Mc-Auth`) en texto plano dentro de los nodos y redundancia de código JavaScript en n8n que es complejo de mantener si la API de Metricool cambia. No hay secretos nuevos.

### Cambios realizados en esta integración
En lugar de crear un script independiente o duplicar el backend, se **modificó la lógica base existente** (`workflow_logic.py` y `metricool_service.py`) para aceptar un parámetro `publication_type`.
1. **`app/config.py`**: Se añadió `STORIES_SHEET_NAME` con valor por defecto `'planificacion_historia'`.
2. **`metricool_service.py`**: El método `create_post` ahora detecta si `publication_type == "STORY"` y adapta el diccionario de datos de Instagram y Facebook antes del envío.
3. **`workflow_logic.py`**: El orquestador puede procesar cualquier nombre de hoja y tipo de publicación, reutilizando la lógica dura.
4. **`main.py`**: El endpoint `/run` ahora lanza dos procesos asíncronos en paralelo usando `BackgroundTasks`: uno procesa Posts y otro procesa Historias de manera independiente pero concurrente.

### Impacto en el comportamiento
- El servidor Cloud Run procesará ambos flujos (Posts e Historias) simultáneamente cada vez que el Scheduler sea invocado.
- El flujo original de Posts es retrocompatible y no sufre alteraciones.
- Se mantiene el principio DRY, resultando en una base de código muy mantenible.
