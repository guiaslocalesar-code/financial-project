"""
Script para crear las tablas en Supabase.
Ejecutar en Cloud Shell con:
    python3 create_tables.py
"""
import asyncio
import os

# Configurar las variables de entorno ANTES de importar la app
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:GuiasSA2020%40@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ENCRYPTION_KEY"] = "hSDDg5gc6wRNz08AzOhfWkWz-lz__Rb_p60iCzdz_qo="

import app.models  # Registra todos los modelos
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    url = os.environ["DATABASE_URL"]
    print(f"🔌 Conectando a Supabase...")
    engine = create_async_engine(url)
    
    async with engine.begin() as conn:
        print("📁 Creando tablas...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ ¡Tablas creadas exitosamente en Supabase!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
