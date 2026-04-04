import os
import asyncio
import asyncpg
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

async def run_migration():
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
    print("1. Conectando a Cloud SQL...")
    try:
        conn = await asyncpg.connect(database_url)
    except Exception as e:
        print(f"Error de conexión a Cloud SQL: {e}")
        return
    
    print("2. Obteniendo datos de user_companies...")
    try:
        rows = await conn.fetch("SELECT * FROM user_companies")
        print(f"-> Se encontraron {len(rows)} registros.")
    except Exception as e:
        print(f"Error al leer la tabla en Cloud SQL: {e}")
        await conn.close()
        return

    await conn.close()
    
    if not rows:
        print("No hay registros para migrar.")
        return

    print("3. Verificando si la tabla existe en Supabase...")
    test_req = requests.get(f"{SUPABASE_URL}/rest/v1/user_companies?limit=1", headers=headers)
    if test_req.status_code == 404:
        print("\nERROR CRÍTICO: La tabla 'user_companies' no existe en Supabase.")
        print("Antes de continuar, debés ejecutar el script SQL en la consola de Supabase.")
        return

    print("4. Migrando datos a Supabase en formato REST...")
    payload = []
    
    for r in rows:
        item = {
            "id": str(r["id"]),
            "user_id": str(r["user_id"]),
            "company_id": str(r["company_id"]),
            "role": r["role"] if r["role"] else "viewer",
            "quotaparte": float(r["quotaparte"]) if r["quotaparte"] is not None else 0,
            "is_active": r["is_active"] if r["is_active"] is not None else True,
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
            "updated_at": r["updated_at"].isoformat() if r.get("updated_at") else None,
        }
        
        # Eliminar keys que sean None para que Supabase use los defaults si corresponde
        item = {k: v for k, v in item.items() if v is not None}
        payload.append(item)

    # Insertar en bloques 
    chunk_size = 500
    success = True
    url = f"{SUPABASE_URL}/rest/v1/user_companies"
    
    for i in range(0, len(payload), chunk_size):
        batch = payload[i:i+chunk_size]
        res = requests.post(url, headers=headers, json=batch)
        
        if res.status_code in (200, 201):
            print(f"-> Batch {i//chunk_size + 1} insertado: {len(batch)} registros.")
        else:
            success = False
            print(f"-> ERROR insertando batch {i//chunk_size + 1}: HTTP {res.status_code}")
            print(res.text)

    if success:
        print("\n¡Migración finalizada con éxito!")
    else:
        print("\nFinalizado con errores en algunos registros.")

if __name__ == "__main__":
    asyncio.run(run_migration())
