"""
Verifica si hay NULLs en columnas obligatorias de 'clients' para una empresa.
"""
import asyncio
from sqlalchemy import create_engine, text

TARGET_URL = "postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

def check_client_data():
    engine = create_engine(TARGET_URL)
    with engine.connect() as conn:
        print("🔍 Auditando TODOS los clientes en Supabase...")
        
        # Conteo total
        total = conn.execute(text("SELECT count(*) FROM clients")).scalar()
        print(f"  - Total clientes en la tabla: {total}")
        
        # Check por columnas críticas
        cols = ['id', 'company_id', 'name', 'cuit_cuil_dni', 'fiscal_condition', 'is_active', 'created_at']
        for col in cols:
            nulls = conn.execute(text(f"SELECT count(*) FROM clients WHERE {col} IS NULL")).scalar()
            print(f"  - {col} es NULL: {nulls} filas")

        # Buscar duplicados de ID (raro pero posible en migraciones fallidas)
        dupes = conn.execute(text("SELECT id, COUNT(*) FROM clients GROUP BY id HAVING COUNT(*) > 1")).fetchall()
        if dupes:
            print(f"  - ⚠️ IDs DUPLICADOS encontrados: {len(dupes)}")

        # Ver los primeros 5 para inspección visual
        print("\n📄 Primeros 5 registros:")
        res = conn.execute(text("SELECT id, name, company_id, is_active, created_at FROM clients LIMIT 5"))
        for row in res:
            print(f"    {row._mapping}")

if __name__ == "__main__":
    check_client_data()
