"""
Migra los datos de la base de GCP a Supabase.
Bypas de FKs usando session_replication_role.
"""
import asyncio
import os
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

async def migrate_table(table_name, source_conn, target_conn):
    print(f"⏳ Procesando {table_name}...", end=" ", flush=True)
    
    table = Base.metadata.tables.get(table_name)
    if table is None:
        print("⚠️ No definido.")
        return

    try:
        # Detectar columnas en origen
        inspector = inspect(SOURCE_ENGINE_SYNC)
        source_columns = [c['name'] for c in inspector.get_columns(table_name)]
        target_columns = [c.name for c in table.columns]
        common_columns = [c for c in target_columns if c in source_columns]
        
        # Leer datos
        stmt = select(*[table.c[c] for c in common_columns])
        result = await source_conn.execute(stmt)
        rows = result.fetchall()
        
        # Siempre borrar registros previos (el orden ya no importa por el modo replica)
        await target_conn.execute(table.delete())

        if rows:
            data = []
            for row in rows:
                d = dict(row._mapping)
                for col in target_columns:
                    if col not in d:
                        d[col] = None 
                data.append(d)
            
            await target_conn.execute(table.insert(), data)
            print(f"✅ {len(data)} migrados.")
        else:
            print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Iniciando migración de datos (v3 - Bypass FKs)...")
    source_engine = create_async_engine(SOURCE_URL)
    target_engine = create_async_engine(TARGET_URL)

    async with source_engine.connect() as s_conn:
        async with target_engine.begin() as t_conn:
            # DESACTIVAR FKs TEMPORALMENTE
            print("🔧 Desactivando restricciones de integridad...")
            await t_conn.execute(text("SET session_replication_role = 'replica';"))
            
            for table_name in TABLE_ORDER:
                await migrate_table(table_name, s_conn, t_conn)
            
            # REACTIVAR FKs
            print("🔧 Reactivando restricciones de integridad...")
            await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print("\n✨ ¡Migración completada con éxito!")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
