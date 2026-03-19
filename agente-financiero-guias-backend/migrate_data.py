"""
Migración TOTAL de 20 tablas de GCP a Supabase.
v8: Control granular (una por una vía argumentos).
"""
import asyncio
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, select, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine

# Supabase
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"
SOURCE_ENGINE_SYNC = create_engine("postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db")
TARGET_ENGINE_SYNC = create_engine("postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres")

def clean_value(col_name, value):
    if value is None: return None
    if col_name in ['cuit', 'cuit_cuil_dni', 'fiscal_id']:
        s_val = str(value)
        if s_val.endswith('.0'): return s_val[:-2]
        return s_val
    return value

async def migrate_table(table_name, s_conn, t_conn, source_metadata):
    print(f"⏳ Procesando {table_name}...", end=" ", flush=True)
    source_table = source_metadata.tables.get(table_name)
    if source_table is None:
        print("❌ No encontrada en origen.")
        return

    try:
        await t_conn.execute(text("SET statement_timeout = '15min';"))
        
        inspector = inspect(TARGET_ENGINE_SYNC)
        if not inspector.has_table(table_name):
            print("🆕 Creando...", end=" ")
            try:
                source_table.create(bind=TARGET_ENGINE_SYNC, checkfirst=True)
            except Exception as e_create:
                if "already exists" in str(e_create).lower():
                    print("(YA EXISTÍA TIPO/TABLA) ", end="")
                else:
                    print(f"⚠️ {str(e_create)[:40]}... ", end="")
            inspector = inspect(TARGET_ENGINE_SYNC)
        
        target_columns = [c['name'] for c in inspector.get_columns(table_name)]
        common_cols = [c.name for c in source_table.columns if c.name in target_columns]

        stmt = select(*[source_table.c[c] for c in common_cols])
        result = await s_conn.execute(stmt)
        rows = result.fetchall()
        
        await t_conn.execute(source_table.delete())
        if rows:
            data = [dict(row._mapping) for row in rows]
            clean_data = []
            for d in data:
                clean_data.append({k: clean_value(k, v) for k, v in d.items()})
            
            await t_conn.execute(source_table.insert().values(clean_data))
            print(f"✅ {len(rows)} migrados.")
        else:
            print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {str(e)[:150]}...")

async def main():
    target_table = sys.argv[1] if len(sys.argv) > 1 else None
    
    print(f"🚀 Iniciando migración {'de ' + target_table if target_table else 'TOTAL (20 tablas)'}...")
    
    source_metadata = MetaData()
    source_metadata.reflect(bind=SOURCE_ENGINE_SYNC)
    
    if target_table:
        tables_to_migrate = [target_table]
    else:
        # Orden de dependencias
        tables_to_migrate = [t.name for t in source_metadata.sorted_tables]
        priority = ['companies', 'users', 'clients', 'payment_methods', 'expense_types', 'services', 'expense_categories']
        tables_to_migrate = [t for t in priority if t in tables_to_migrate] + [t for t in tables_to_migrate if t not in priority]

    source_engine_async = create_async_engine(SOURCE_URL)
    target_engine_async = create_async_engine(TARGET_URL)

    async with source_engine_async.connect() as s_conn:
        async with target_engine_async.begin() as t_conn:
            await t_conn.execute(text("SET session_replication_role = 'replica';"))
            await t_conn.execute(text("SET statement_timeout = '15min';"))
            
            for t_name in tables_to_migrate:
                await migrate_table(t_name, s_conn, t_conn, source_metadata)
            
            await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print(f"\n✨ ¡Migración {'de ' + target_table if target_table else 'TOTAL'} FINALIZADA!")
    await source_engine_async.dispose()
    await target_engine_async.dispose()

if __name__ == "__main__":
    asyncio.run(main())
