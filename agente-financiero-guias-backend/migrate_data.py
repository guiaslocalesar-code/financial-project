"""
Migración TOTAL de 20 tablas de GCP a Supabase.
v7: Timeout masivo (15m), checkfirst=True y manejo de tipos existentes.
"""
import asyncio
import os
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
        # Aumentar timeout por tabla en el destino
        await t_conn.execute(text("SET statement_timeout = '15min';"))
        
        inspector = inspect(TARGET_ENGINE_SYNC)
        if not inspector.has_table(table_name):
            print("🆕 Creando...", end=" ")
            try:
                # Usamos checkfirst=True para evitar errores si algo medio existe
                source_table.create(bind=TARGET_ENGINE_SYNC, checkfirst=True)
            except Exception as e_create:
                if "already exists" in str(e_create).lower():
                    print("(YA EXISTÍA TIPO) ", end="")
                else:
                    print(f"⚠️ Error creación: {str(e_create)[:50]}... ", end="")
            
            # Refrescar inspector después de intentar crear
            inspector = inspect(TARGET_ENGINE_SYNC)
        
        target_columns = [c['name'] for c in inspector.get_columns(table_name)]
        common_cols = [c.name for c in source_table.columns if c.name in target_columns]

        # Leer del origen
        stmt = select(*[source_table.c[c] for c in common_cols])
        result = await s_conn.execute(stmt)
        rows = result.fetchall()
        
        # Limpiar y Cargar
        await t_conn.execute(source_table.delete())
        if rows:
            data = []
            for row in rows:
                d = dict(row._mapping)
                clean_d = {k: clean_value(k, v) for k, v in d.items()}
                data.append(clean_d)
            
            # Inserción por lotes para mayor eficiencia
            await t_conn.execute(source_table.insert().values(data))
            print(f"✅ {len(data)} migrados.")
        else:
            print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {str(e)[:150]}...")

async def main():
    print("🚀 Inicia Migración v7 (Residencial + Robustez)...")
    
    # Reflexión del origen con timeout largo
    print("📋 Escaneando origen...")
    source_metadata = MetaData()
    source_metadata.reflect(bind=SOURCE_ENGINE_SYNC)
    tables = [t.name for t in source_metadata.sorted_tables]

    # Orden forzado para minimizar problemas de FK (aunque usamos replica mode)
    priority_tables = ['companies', 'users', 'clients', 'payment_methods', 'expense_types', 'services']
    other_tables = [t for t in tables if t not in priority_tables]
    tables_ordered = [t for t in priority_tables if t in tables] + other_tables

    source_engine_async = create_async_engine(SOURCE_URL)
    target_engine_async = create_async_engine(TARGET_URL)

    async with source_engine_async.connect() as s_conn:
        async with target_engine_async.begin() as t_conn:
            print("🔧 SETTINGS: replica=on, timeout=15m")
            await t_conn.execute(text("SET session_replication_role = 'replica';"))
            await t_conn.execute(text("SET statement_timeout = '15min';"))
            
            for t_name in tables_ordered:
                await migrate_table(t_name, s_conn, t_conn, source_metadata)
            
            await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print("\n✨ ¡FIN DE LA MIGRACIÓN v7!")
    await source_engine_async.dispose()
    await target_engine_async.dispose()

if __name__ == "__main__":
    asyncio.run(main())
