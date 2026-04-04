# NORMALIZAR IDs OFICIALES

Reescribe los UUIDs aleatorios asignados durante la migración con los IDs oficiales del sistema original.

## ¿Qué hace?

| Tabla | Antes | Después |
|---|---|---|
| `services.id` | UUID random | `45311`, `45413`, etc. |
| `clients.id` | UUID random | `c2`, `c3`, etc. |
| `client_services` | UUIDs random | IDs oficiales según el CSV |
| FKs en `income_budgets`, `transactions`, `invoices`, `invoice_items` | UUIDs | IDs oficiales |

## CSVs requeridos

Deben estar en `csvs para reemplazar ids/`:

| Archivo | Función |
|---|---|
| `FLUJO DE DINERO NEW - Servicios.csv` | IDs oficiales de servicios |
| `FLUJO DE DINERO NEW - manual de marca finanzas.csv` | IDs oficiales de clientes + relación cliente↔servicio |

## Antes de ejecutar

1. ✅ Asegurate de que los CSVs están en `csvs para reemplazar ids/`
2. ✅ Hacé un backup manual si querés doble seguridad (el script hace uno automático)
3. ✅ Asegurate de que `.env` tiene `DATABASE_URL` configurado

## Ejecutar

```bash
# Desde la raíz del proyecto (ATG_agente financiero/)
python -m Migracion.normalizar_ids_oficiales
```

## Idempotencia

El script detecta automáticamente si los IDs ya fueron normalizados y hace **skip** si es así. Es seguro ejecutar más de una vez.

## Resultado esperado (log de salida)

```
============================================================
  NORMALIZAR IDs OFICIALES
============================================================
📂 PASO 1: Leyendo CSVs...
  → 13 servicios únicos en CSV
  → 28 clientes ACTIVOS | 38 total en CSV
🔍 Verificando idempotencia...
  → IDs en formato UUID detectados. Procediendo...
🔧 PASO 3: Alterando tipos de columna UUID → VARCHAR...
🛠️  PASO 4: Actualizando services...
  ✅ Services actualizados: 13 | Sin match: 0
👤 PASO 5: Actualizando clients...
  ✅ Clients actualizados: N | Sin match: 0
🔗 PASO 6: Actualizando FKs...
🔗 PASO 7: Reconstruyendo client_services...
✅ PASO 8: Verificaciones de integridad...
  🎉 ¡INTEGRIDAD PERFECTA! Todas las FKs son válidas.
============================================================
  ✅ NORMALIZACIÓN COMPLETADA EXITOSAMENTE
============================================================
```

## Verificar post-ejecución

```sql
-- Servicios con IDs oficiales
SELECT id, name FROM services ORDER BY id;

-- Clientes con IDs oficiales
SELECT id, name FROM clients ORDER BY id;

-- Cliente c3 Import con sus servicios
SELECT cs.client_id, cs.service_id, s.name
FROM client_services cs
JOIN services s ON cs.service_id = s.id
WHERE cs.client_id = 'c3';

-- 0 FKs rotas en income_budgets
SELECT COUNT(*) FROM income_budgets ib
WHERE NOT EXISTS (SELECT 1 FROM clients c WHERE c.id = ib.client_id);
```

## Nota sobre modelos SQLAlchemy

Después de ejecutar este script, los modelos `Service` y `Client` en `app/models/` siguen declarando `id: Mapped[uuid.UUID]`. Esto funciona en runtime porque PostgreSQL acepta el cast automático, pero para mantener la coherencia del código se recomienda actualizar los modelos a `id: Mapped[str] = mapped_column(String, primary_key=True)`.
