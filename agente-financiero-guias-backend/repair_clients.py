"""
Repara datos de la tabla 'clients' que puedan estar rompiendo el backend (NULLs en updated_at o emails inválidos).
"""
import asyncio
from sqlalchemy import create_engine, text

TARGET_URL = "postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

def repair_client_data():
    engine = create_engine(TARGET_URL)
    with engine.connect() as conn:
        print("🛠️ Reparando datos de clientes...")
        
        # 1. Llenar updated_at si es NULL
        res = conn.execute(text("UPDATE clients SET updated_at = created_at WHERE updated_at IS NULL"))
        print(f"  - updated_at reparados: {res.rowcount}")

        # 2. Limpiar emails inválidos (si tienen 'none', o no tienen @, poner NULL)
        res = conn.execute(text("UPDATE clients SET email = NULL WHERE email IS NOT NULL AND (email NOT LIKE '%@%' OR email = 'none')"))
        print(f"  - emails inválidos limpiados: {res.rowcount}")

        # 3. Llenar is_active si es NULL (por seguridad)
        res = conn.execute(text("UPDATE clients SET is_active = true WHERE is_active IS NULL"))
        print(f"  - is_active defaults aplicados: {res.rowcount}")

        conn.commit()
    print("✨ Reparación finalizada.")

if __name__ == "__main__":
    repair_client_data()
