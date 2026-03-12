# MIGRACIÓN HISTÓRICO FINANCIERO

## Requisitos
- Archivo `.env` configurado apuntando a la base de datos destino local o en Cloud SQL.
- Base de datos con todas las tablas creadas (correr Alembic previamente).
- Archivos `.csv` ubicados en la carpeta `Migracion/`.

## Ejecutar
Para procesar la migración de forma secuencial y estructurada, ejecuta los siguientes comandos desde la raíz del proyecto backend:

```bash
# Entorno virtual
# source venv/bin/activate (Linux/Mac) o venv\Scripts\activate (Windows)

# 1. Catálogos (Servicios, Tipos de Egresos, Categorías)
python -m Migracion.migracion_catalogos

# 2. Entradas/Ingresos (Clientes, Presupuestos de Ingreso, Transacciones de Ingreso)
python -m Migracion.migracion_ingresos  

# 3. Salidas/Egresos (Presupuestos de Egreso, Transacciones de Egreso)
python -m Migracion.migracion_egresos
```

## Verificación
Una vez finalizado, puedes conectar a la base de datos y verificar que los números coincidan aproximadamente con las cifras esperadas.

```sql
SELECT COUNT(*) FROM transactions WHERE type='income';   -- → ~1200
SELECT COUNT(*) FROM transactions WHERE type='expense';  -- → ~400  
SELECT COUNT(*) FROM income_budgets WHERE status='COLLECTED'; -- → ~1200
```

> **NOTA:** La migración es **IDEMPOTENTE**. Puedes ejecutar los scripts todas las veces que desees. El sistema detectará los registros duplicados validando datos clave antes de la inserción y los omitirá.
