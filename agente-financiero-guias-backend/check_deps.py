"""
Verifica si existen las tablas de dependencia.
"""
import asyncio
import os
from sqlalchemy import create_engine, inspect

TARGET_URL = "postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

def check_tables():
    engine = create_engine(TARGET_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tablas actuales en Supabase: {len(tables)}")
    deps = ['payment_methods', 'companies', 'users', 'transactions']
    for d in deps:
        exists = d in tables
        print(f"  - {d}: {'✅' if exists else '❌'}")

if __name__ == "__main__":
    check_tables()
