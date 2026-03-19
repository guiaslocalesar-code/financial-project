"""
Migración TOTAL de 20 tablas de GCP a Supabase.
Manejo correcto de conexiones y limpieza de datos.
"""
import asyncio
import os
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, select, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine

# Variables de entorno
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

# URLs
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"
SOURCE_ENGINE_SYNC = create_engine("postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db")
TARGET_ENGINE_SYNC = create_engine("postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres")

def clean_value(col_name, value):
    if value is None:
        return None
    if col_name in ['cuit', 'cuit_cuil_dni', 'fiscal_id']:
        s_val = str(value)
        if s_val.endswith('.0'):
            return s_val[:-2]
        return s_val
    return value

async def migrate_table(table_name, s_conn, t_conn, source_metadata):
    print(f"⏳ Procesando {table_name}...", end=" ", flush=True)
    
    source_table = source_metadata.tables.get(table_name)
    if source_table is None:
        print("❌ No encontrada en origen.")
        return

    try:
        # 1. Asegurar existencia en el destino (Sincrónico)
        inspector = inspect(TARGET_ENGINE_SYNC)
        if not inspector.has_table(table_name):
            print("🆕 Creando...", end=" ")
            source_table.create(bind=TARGET_ENGINE_SYNC)
        
        # 2. Obtener columnas del destino para evitar errores de columnas faltantes
        target_columns = [c['name'] for c in inspector.get_columns(table_name)]
        source_cols = [c.name for c in source_table.columns]
        common_cols = [c for c in source_cols if c in target_columns]

        # 3. Leer datos
        stmt = select(*[source_table.c[c] for c in common_cols])
        result = await s_conn.execute(stmt)
        rows = result.fetchall()
        
        # 4. Limpiar destino
        await t_conn.execute(source_table.delete())

        if rows:
            now = datetime.now()
            data = []
            for row in rows:
                d = dict(row._mapping)
                clean_d = {k: clean_value(k, v) for k, v in d.items()}
                # Rellenar obligatorios si faltan
                # (Asumimos que la tabla de destino tiene las mismas columnas que common_cols o defaults)
                data.append(clean_d)
            
            # Usar INSERT dinámico con solo las columnas comunes
            await t_conn.execute(source_table.insert().values(data))
            print(f"✅ {len(data)} migrados.")
        else:
            print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Iniciando MIGRACIÓN TOTAL (20 tablas) - v5...")
    
    source_metadata = MetaData()
    source_metadata.reflect(bind=SOURCE_ENGINE_SYNC)
    tables_to_migrate = [t.name for t in source_metadata.sorted_tables]

    source_engine_async = create_async_engine(SOURCE_URL)
    target_engine_async = create_async_engine(TARGET_URL)

    async with source_engine_async.connect() as s_conn:
        async with target_engine_async.begin() as t_conn:
            print("🔧 Modo réplica: ON")
            await t_conn.execute(text("SET session_replication_role = 'replica';"))
            
            for table_name in tables_to_migrate:
                await migrate_table(table_name, s_conn, t_conn, source_metadata)
            
            print("🔧 Modo réplica: OFF")
            await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print("\n✨ ¡MIGRACIÓN TOTAL FINALIZADA!")
    await source_engine_async.dispose()
    await target_engine_async.dispose()

if __name__ == "__main__":
    asyncio.run(main())
