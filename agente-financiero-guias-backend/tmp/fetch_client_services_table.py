import asyncio
import os
from sqlalchemy import text
from app.database import engine
import pandas as pd

async def fetch_client_services():
    query = text("""
        SELECT 
            c.name AS CLIENTE,
            s.name AS SERVICIO,
            cs.monthly_fee AS COSTO,
            cs.status AS ESTADO
        FROM clients c
        JOIN client_services cs ON c.id = cs.client_id
        JOIN services s ON s.id = cs.service_id
        ORDER BY c.name, s.name;
    """)
    
    async with engine.connect() as conn:
        result = await conn.execute(query)
        rows = result.fetchall()
        
    df = pd.DataFrame(rows, columns=['CLIENTE', 'SERVICIO', 'COSTO', 'ESTADO'])
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    asyncio.run(fetch_client_services())
