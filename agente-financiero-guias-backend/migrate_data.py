"""
Migración TOTAL de 20 tablas de GCP a Supabase.
Usa Reflexión para manejar tablas no definidas en el código.
"""
import asyncio
import os
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, select, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine

# Variables de entorno para Supabase
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

# URLs
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"
# Motores Sincrónicos (necesarios para reflexión)
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

async def migrate_table(table_name, source_engine, target_engine, source_metadata):
    print(f"⏳ Procesando {table_name}...", end=" ", flush=True)
    
    # Obtener tabla por reflexión del origen
    source_table = source_metadata.tables.get(table_name)
    if source_table is None:
        print("❌ No encontrada en origen.")
        return

    try:
        # 1. Asegurar que la tabla existe en el destino (Sui Generis Reflection/Creation)
        target_metadata = MetaData()
        target_metadata.reflect(bind=TARGET_ENGINE_SYNC, only=[table_name])
        
        if table_name not in target_metadata.tables:
            print("🆕 Creando tabla en destino...", end=" ")
            # Intentar crear la tabla en destino con el esquema del origen
            source_table.to_metadata(target_metadata)
            target_metadata.create_all(bind=TARGET_ENGINE_SYNC)

        # 2. Leer datos del origen
        async with source_engine.connect() as s_conn:
            stmt = select(source_table)
            result = await s_conn.execute(stmt)
            rows = result.fetchall()
            
            # 3. Insertar en destino
            async with target_engine.begin() as t_conn:
                # Borrar registros previos
                await t_conn.execute(source_table.delete())
                
                if rows:
                    data = []
                    now = datetime.now()
                    for row in rows:
                        d = dict(row._mapping)
                        clean_d = {k: clean_value(k, v) for k, v in d.items()}
                        # Defaults básicos para timestamps si faltan
                        for col in source_table.columns:
                            if col.name not in clean_d or clean_d[col.name] is None:
                                if not col.nullable and not col.primary_key:
                                    if 'date' in col.name or 'at' in col.name:
                                        clean_d[col.name] = now
                        data.append(clean_d)
                    
                    await t_conn.execute(source_table.insert(), data)
                    print(f"✅ {len(data)} migrados.")
                else:
                    print("⚠️ Vacía.")

    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🚀 Iniciando MIGRACIÓN TOTAL (20 tablas)...")
    
    # Reflexión completa del origen
    print("📋 Escaneando esquema del origen...")
    source_metadata = MetaData()
    source_metadata.reflect(bind=SOURCE_ENGINE_SYNC)
    
    # Ordenamos por dependencias según la reflexión
    tables_to_migrate = [t.name for t in source_metadata.sorted_tables]
    print(f"📦 Orden de migración detectado: {', '.join(tables_to_migrate)}")

    source_engine_async = create_async_engine(SOURCE_URL)
    target_engine_async = create_async_engine(TARGET_URL)

    async with target_engine_async.begin() as t_conn:
        print("🔧 Activando modo réplica (bypass FKs)...")
        await t_conn.execute(text("SET session_replication_role = 'replica';"))
        
        for table_name in tables_to_migrate:
            await migrate_table(table_name, source_engine_async, target_engine_async, source_metadata)
        
        print("🔧 Desactivando modo réplica...")
        await t_conn.execute(text("SET session_replication_role = 'origin';"))

    print("\n✨ ¡MIGRACIÓN TOTAL COMPLETADA!")
    await source_engine_async.dispose()
    await target_engine_async.dispose()

if __name__ == "__main__":
    asyncio.run(main())
