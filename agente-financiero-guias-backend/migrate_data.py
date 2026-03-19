"""
Migra los datos de la base de GCP a Supabase.
Ejecutar en Cloud Shell:
    python3 migrate_data.py
"""
import asyncio
import os
import traceback

# Variables de entorno para bypass de Pydantic
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ENCRYPTION_KEY"] = "hSDDg5gc6wRNz08AzOhfWkWz-lz__Rb_p60iCzdz_qo="

import app.models
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select

# URLs
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:GuiasSA2020@34.39.132.36/postgres"

async def main():
    print("🚀 Iniciando migración de datos...")
    print(f"🔹 Origen: GCP (34.39.132.36)")
    print(f"🔸 Destino: Supabase")

    source_engine = create_async_engine(SOURCE_URL)
    target_engine = create_async_engine(TARGET_URL)

    # Test connection to Source
    print("\n🔌 Probando conexión al origen...")
    try:
        async with source_engine.connect() as conn:
            print("  ✅ Conexión al origen exitosa.")
    except Exception as e:
        print(f"  ❌ Error conectando al ORIGEN: {e}")
        traceback.print_exc()
        return

    tables = Base.metadata.sorted_tables
    
    for table in tables:
        print(f"\n⏳ Copiando tabla: {table.name}...")
        try:
            async with source_engine.connect() as s_conn:
                result = await s_conn.execute(select(table))
                rows = result.fetchall()
                if rows:
                    async with target_engine.begin() as t_conn:
                        # Limpiar tabla destino antes de insertar
                        await t_conn.execute(table.delete())
                        data = [dict(row._mapping) for row in rows]
                        await t_conn.execute(table.insert(), data)
                        print(f"  ✅ {len(data)} registros copiados")
                else:
                    print(f"  ⚠️ Tabla vacía en origen, saltando...")
        except Exception as e:
            print(f"  ❌ Error en tabla {table.name}: {e}")
            traceback.print_exc()

    print("\n✨ ¡Migración completada!")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
