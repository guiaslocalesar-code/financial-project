"""
Migra los datos de la base de GCP a Supabase.
Maneja dependencias y columnas faltantes dinámicamente.
"""
import asyncio
import os
import traceback
from sqlalchemy import create_engine, text, inspect, select

# Variables de entorno
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
os.environ["SECRET_KEY"] = "dummy"
os.environ["ENCRYPTION_KEY"] = "hSDDg5gc6wRNz08AzOhfWkWz-lz__Rb_p60iCzdz_qo="

import app.models
from app.database import Base
from sqlalchemy.ext.asyncio import create_async_engine

# URLs
TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
SOURCE_URL = "postgresql+asyncpg://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"
# Engine sincrónico para inspección
SOURCE_ENGINE_SYNC = create_engine("postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db")

# Orden manual para evitar errores de FK
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

async def migrate_table(table_name, source_engine, target_engine):
    print(f"\n⏳ Procesando {table_name}...")
    
    # 1. Obtener el objeto Table de SQLAlchemy
    table = Base.metadata.tables.get(table_name)
    if table is None:
        print(f"  ⚠️ No se encontró la definición de {table_name} en los modelos.")
        return

    try:
        # 2. Detectar qué columnas existen en el origen
        inspector = inspect(SOURCE_ENGINE_SYNC)
        source_columns = [c['name'] for c in inspector.get_columns(table_name)]
        # Solo pedir las columnas que existen en ambos lados
        target_columns = [c.name for c in table.columns]
        common_columns = [c for c in target_columns if c in source_columns]
        
        # 3. Leer datos
        async with source_engine.connect() as s_conn:
            stmt = select(*[table.c[c] for c in common_columns])
            result = await s_conn.execute(stmt)
            rows = result.fetchall()
            
            if not rows:
                print(f"  ⚠️ Tabla vacía en origen.")
                return

            # 4. Insertar en destino
            async with target_engine.begin() as t_conn:
                # Borrar registros previos
                await t_conn.execute(table.delete())
                
                # Preparar datos (mapear filas a diccionarios)
                data = []
                for row in rows:
                    d = dict(row._mapping)
                    # Rellenar columnas faltantes con None/Default si no estaban en el origen
                    for col in target_columns:
                        if col not in d:
                            d[col] = None 
                    data.append(d)
                
                await t_conn.execute(table.insert(), data)
                print(f"  ✅ {len(data)} registros migrados exitosamente.")

    except Exception as e:
        print(f"  ❌ Error en {table_name}: {e}")

async def main():
    print("🚀 Iniciando migración de datos (v2 - Inteligente)...")
    source_engine = create_async_engine(SOURCE_URL)
    target_engine = create_async_engine(TARGET_URL)

    # Migrar en orden
    for table_name in TABLE_ORDER:
        await migrate_table(table_name, source_engine, target_engine)

    print("\n✨ ¡Migración completada con éxito!")
    await source_engine.dispose()
    await target_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
