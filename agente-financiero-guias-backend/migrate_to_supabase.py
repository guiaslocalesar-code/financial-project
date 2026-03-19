import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text
from app.database import Base
from app.config import settings
import sys
import app.models # Crucial: Imports all models to register them with Base.metadata

# Current GCP DB
SOURCE_URL = settings.async_database_url

async def migrate(source_url: str, target_url: str):
    print(f"🚀 Iniciando migración de \n🔹 Origen: {source_url} \n🔸 Destino: {target_url}...")
    
    source_engine = create_async_engine(source_url)
    target_engine = create_async_engine(target_url)
    
    # 1. Create tables in target
    async with target_engine.begin() as conn:
        print("📁 Creando tablas en el destino...")
        await conn.run_sync(Base.metadata.create_all)
    
    # ... (rest of the logic stays the same)
    # ... (skipping some lines for brevity in replace_file_content is not allowed, I'll provide the whole block)
    tables = Base.metadata.sorted_tables
    for table in tables:
        print(f"⏳ Copiando tabla: {table.name}...")
        async with source_engine.connect() as s_conn:
            result = await s_conn.execute(select(table))
            rows = result.fetchall()
            if rows:
                async with target_engine.begin() as t_conn:
                    data = [dict(row._mapping) for row in rows]
                    await t_conn.execute(table.insert(), data)
                    print(f"✅ {len(data)} registros copiados")
    
    print("\n✨ Migración completada con éxito.")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python migrate_to_supabase.py <target_url> <source_url>")
    else:
        target = sys.argv[1]
        source = sys.argv[2]
        
        def fix_url(url):
            if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        asyncio.run(migrate(fix_url(source), fix_url(target)))
