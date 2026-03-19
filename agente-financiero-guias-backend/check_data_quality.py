"""
Verifica la validez de los correos electrónicos en la base de datos de Supabase.
Si hay correos inválidos, el Pydantic del backend puede tirar 500 al intentar serializar.
"""
import asyncio
import os
from sqlalchemy import create_engine, text

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres'

def check_emails():
    engine = create_engine('postgresql://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres')
    with engine.connect() as conn:
        print("🔍 Buscando correos potencialmente inválidos...")
        res = conn.execute(text("SELECT id, name, email FROM clients WHERE email IS NOT NULL AND email != ''"))
        clients = res.fetchall()
        
        invalid_count = 0
        for c in clients:
            email = c[2]
            if '@' not in email or '.' not in email.split('@')[-1]:
                print(f"  ❌ Cliente {c[0]} ({c[1]}): Correo inválido '{email}'")
                invalid_count += 1
        
        if invalid_count == 0:
            print("  ✅ Todos los correos parecen tener formato básico válido (@ y .)")
        else:
            print(f"  ⚠️ Se encontraron {invalid_count} correos inválidos.")

        # Check for .0 in CUIT
        res = conn.execute(text("SELECT count(*) FROM clients WHERE cuit_cuil_dni LIKE '%.0'"))
        cuit_count = res.scalar()
        print(f"\n📑 Clientes con '.0' en el CUIT: {cuit_count}")

if __name__ == "__main__":
    check_emails()
