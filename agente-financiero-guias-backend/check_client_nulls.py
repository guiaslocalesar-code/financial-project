"""
Verifica si hay valores NULL en columnas obligatorias de 'clients'.
"""
import asyncio
import os
from sqlalchemy import create_engine, text

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres'

def check_nulls():
    engine = create_engine('postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres')
    with engine.connect() as conn:
        print("🔍 Buscando NULLs en columnas obligatorias...")
        
        cols = ['created_at', 'updated_at', 'is_active', 'fiscal_condition']
        for col in cols:
            res = conn.execute(text(f"SELECT count(*) FROM clients WHERE {col} IS NULL"))
            count = res.scalar()
            print(f"  - {col}: {count} NULLs")
            
        # Check for fiscal_condition validity
        res = conn.execute(text("SELECT DISTINCT fiscal_condition FROM clients"))
        vals = [r[0] for r in res]
        print(f"\n📂 Valores en fiscal_condition: {vals}")

if __name__ == "__main__":
    check_nulls()
