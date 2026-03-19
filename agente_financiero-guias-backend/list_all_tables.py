"""
Lista TODAS las tablas en 'agente_financiero_db'.
"""
import asyncio
import os
from sqlalchemy import create_engine, inspect

SOURCE_URL = "postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"

def list_all():
    engine = create_engine(SOURCE_URL)
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema='public')
        print(f"📊 Se encontraron {len(tables)} tablas en 'agente_financiero_db':")
        for t in sorted(tables):
            print(f"  - {t}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_all()
