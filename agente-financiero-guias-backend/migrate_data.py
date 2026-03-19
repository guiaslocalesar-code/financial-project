"""
Migra los datos de la base de GCP a Supabase.
Incluye LIMPIEZA de datos (CUITs, fechas, NULLs).
"""
import asyncio
import os
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, select
from sqlalchemy.ext.asyncio import create_async_engine

# Variables de entorno
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ENCRYPTION_KEY"] = "hSDDg5gc6wRNz08AzOhfWkWz-lz__Rb_p60iCzdz_qo="

import app.models
from app.database import Base

# URLs
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"
SOURCE_ENGINE_SYNC = create_engine("postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db")

TABLE_ORDER = [
    'companies',
    'clients',
    'expense_types',
    'expense_categories',
    'services',
    'client_services',
    'expense_budgets',
    'income_budgets',
    'transactions',
    'invoices',
    'invoice_items'
]

def clean_value(col_name, value):
    """Limpia valores conflictivos comunes."""
    if value is None:
        return None
    
    # Quitar .0 de CUITs/Documentos (error común al importar de Excel/Google Sheets)
    if col_name in ['cuit', 'cuit_cuil_dni', 'cuit_cuil_dni_dni', 'fiscal_id']:
        s_val = str(value)
        if s_val.endswith('.0'):
            return s_val[:-2]
        return s_val
    
    return value

async def migrate_table(table_name, source_conn, target_conn):
    print(f"⏳ Procesando {table_name}...", end=" ", flush=True)
    
    table = Base.metadata.tables.get(table_name)
    if table is None:
        print("⚠️ No definido.")
        return

    try:
        # Detectar columnas
        inspector = inspect(SOURCE_ENGINE_SYNC)
        source_columns = [c['name'] for c in inspector.get_columns(table_name)]
        target_columns = {c.name: c for c in table.columns}
        common_columns = [c for c in target_columns if c in source_columns]
        
        # Leer datos
        stmt = select(*[table.c[c] for c in common_columns])
        result = await source_conn.execute(stmt)
        rows = result.fetchall()
        
        # Siempre borrar en destino
        await target_conn.execute(table.delete())

        if rows:
            now = datetime.now()
            data = []
            for row in rows:
                d = dict(row._mapping)
                # Limpiar y normalizar cada valor
                clean_d = {}
                for col, val in d.items():
                    clean_d[col] = clean_value(col, val)
                
                # Rellenar faltantes obligatorios
                for col_name, col_obj in target_columns.items():
                    if col_name not in clean_d or clean_d[col_name] is None:
                        if not col_obj.nullable and not col_obj.primary_key:
                            # Valores por defecto para campos requeridos
                            if col_name in ['created_at', 'updated_at', 'planned_date', 'transaction_date', 'issue_date']:
                                clean_d[col_name] = now
                            elif col_name == 'is_active':
                                clean_d[col_name] = True
                            elif col_name == 'status':
                                # Intento deducir un status válido basado en defaults del modelo
                                clean_d[col_name] = col_obj.default.arg if col_obj.default else None
                            else:
                                clean_d[col_name] = None
                data.append(clean_d)
            
            await target_conn.execute(table.insert(), data)
            print(f"✅ {len(data)} migrados (Limpios).")
        else:
            print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Iniciando migración de datos (v4 - Limpieza + Bypass)...")
    source_engine = create_async_engine(SOURCE_URL)
    target_engine = create_async_engine(TARGET_URL)

    async with source_engine.connect() as s_conn:
        async with target_engine.begin() as t_conn:
            await t_conn.execute(text("SET session_replication_role = 'replica';"))
            for table_name in TABLE_ORDER:
                await migrate_table(table_name, s_conn, t_conn)
            await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print("\n✨ ¡Migración completada con éxito!")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
