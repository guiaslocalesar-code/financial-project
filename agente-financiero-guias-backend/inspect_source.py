"""
Diagnóstico de la base de datos de origen (GCP).
Lista todas las bases de datos y tablas disponibles.
"""
import asyncio
import os
from sqlalchemy import create_engine, text

# URL del Proxy
SOURCE_URL_BASE = "postgresql://postgres:FinancialAgent_2026!@127.0.0.1:5434/"

def inspect():
    print("🔍 Inspeccionando instancia de GCP...")
    
    # 1. Listar Bases de Datos
    engine = create_engine(SOURCE_URL_BASE + "postgres")
    try:
        with engine.connect() as conn:
            print("\n📂 Bases de datos disponibles:")
            res = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            for r in res:
                print(f"  - {r[0]}")
            
            # 2. Listar Esquemas en 'postgres'
            print("\n🗺️ Esquemas en 'postgres':")
            res = conn.execute(text("SELECT schema_name FROM information_schema.schemata;"))
            for r in res:
                print(f"  - {r[0]}")
                
            # 3. Listar Tablas en 'public'
            print("\n📋 Tablas en 'postgres.public':")
            res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
            tables = res.fetchall()
            if tables:
                for r in tables:
                    print(f"  - {r[0]}")
            else:
                print("  (Ninguna tabla encontrada en el esquema public)")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect()
