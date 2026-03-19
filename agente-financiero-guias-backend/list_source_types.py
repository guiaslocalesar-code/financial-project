"""
Identifica tipos de datos personalizados (Enums) en el origen.
"""
import asyncio
import os
from sqlalchemy import create_engine, text

SOURCE_URL = "postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/agente_financiero_db"

def list_types():
    engine = create_engine(SOURCE_URL)
    with engine.connect() as conn:
        print("🔍 Buscando tipos de datos personalizados...")
        res = conn.execute(text("SELECT n.nspname as schema, t.typname as type FROM pg_type t LEFT JOIN pg_namespace n ON n.oid = t.typnamespace WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_class c WHERE c.oid = t.typrelid)) AND NOT EXISTS(SELECT 1 FROM pg_type el WHERE el.oid = t.typelem AND el.typbasetype = t.oid) AND n.nspname NOT IN ('pg_catalog', 'information_schema') AND t.typname NOT LIKE '\\_%'"))
        types = res.fetchall()
        for t in types:
            print(f"  - {t[0]}.{t[1]}")

if __name__ == "__main__":
    list_types()
