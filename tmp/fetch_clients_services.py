import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_data():
    database_url = os.getenv("DATABASE_URL")
    # Convert sqlalchemy asyncpg url to asyncpg url
    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(database_url)
    
    query = """
    SELECT 
        c.name as client_name,
        s.name as service_name,
        cs.monthly_fee,
        cs.currency,
        cs.status::text as status
    FROM 
        client_services cs
    JOIN 
        clients c ON cs.client_id = c.id
    JOIN 
        services s ON cs.service_id = s.id
    ORDER BY 
        c.name, s.name;
    """
    
    rows = await conn.fetch(query)
    
    print("| Cliente | Servicio | Monto | Moneda | Estado |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    for row in rows:
        print(f"| {row['client_name']} | {row['service_name']} | {row['monthly_fee']} | {row['currency']} | {row['status']} |")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
