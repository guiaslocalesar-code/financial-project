-- =============================================================
-- Migración: Facturación Opcional (Blanco/Negro) + IVA
-- Ejecutar en el SQL Editor de Supabase
-- =============================================================

-- 1. CLIENTS: Agregar columna requires_invoice (default: true = en blanco)
ALTER TABLE clients
ADD COLUMN IF NOT EXISTS requires_invoice BOOLEAN NOT NULL DEFAULT true;

-- 2. INCOME_BUDGETS: Agregar requires_invoice, iva_rate, iva_amount
ALTER TABLE income_budgets
ADD COLUMN IF NOT EXISTS requires_invoice BOOLEAN NOT NULL DEFAULT true;

ALTER TABLE income_budgets
ADD COLUMN IF NOT EXISTS iva_rate NUMERIC(5,2) DEFAULT 0.0;

ALTER TABLE income_budgets
ADD COLUMN IF NOT EXISTS iva_amount NUMERIC(12,2) DEFAULT 0.0;

-- 3. TRANSACTIONS: Agregar requires_invoice, iva_rate, iva_amount
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS requires_invoice BOOLEAN NOT NULL DEFAULT true;

ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS iva_rate NUMERIC(5,2) DEFAULT 0.0;

ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS iva_amount NUMERIC(12,2) DEFAULT 0.0;

-- 4. DATA MIGRATION: Marcar Limbox como "en negro" (sin factura)
UPDATE clients
SET requires_invoice = false
WHERE LOWER(name) LIKE '%limbox%';

-- 5. Verificación
SELECT id, name, requires_invoice FROM clients ORDER BY name;
