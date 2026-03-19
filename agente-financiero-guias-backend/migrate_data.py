"""
Migra los datos de la base de GCP a Supabase.
Usa Cloud SQL Proxy para la conexión segura.
"""
import asyncio
import os
import traceback

# Variables de entorno
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ENCRYPTION_KEY"] = "hSDDg5gc6wRNz08AzOhfWkWz-lz__Rb_p60iCzdz_qo="

import app.models
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select

# URLs - USANDO EL PROXY EN EL PUERTO 5434
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/postgres"

async def main():
    print("🚀 Iniciando migración de datos vía Proxy...")
    print(f"🔹 Origen: GCP (vía Proxy 5434)")
    print(f"🔸 Destino: Supabase")

    source_engine = create_async_engine(SOURCE_URL)
    target_engine = create_async_engine(TARGET_URL)

    print("\n🔌 Probando conexión al ORIGEN (localhost:5434)...")
    try:
        async with source_engine.connect() as conn:
            print("  ✅ Conexión exitosa al origen!")
    except Exception as e:
        print(f"  ❌ Error de conexión al ORIGEN: {e}")
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
                        await t_conn.execute(table.delete())
                        data = [dict(row._mapping) for row in rows]
                        await t_conn.execute(table.insert(), data)
                        print(f"  ✅ {len(data)} registros copiados")
                else:
                    print(f"  ⚠️ Tabla vacía, saltando...")
        except Exception as e:
            print(f"  ❌ Error en {table.name}: {e}")

    print("\n✨ ¡Migración completada!")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
