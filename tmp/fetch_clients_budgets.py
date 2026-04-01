import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_data():
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(database_url)
    
    # We'll take the latest budgeted_amount for each client/service
    query = """
    WITH LatestBudgets AS (
        SELECT 
            client_id, 
            service_id, 
            budgeted_amount,
            period_year,
            period_month,
            ROW_NUMBER() OVER(PARTITION BY client_id, service_id ORDER BY period_year DESC, period_month DESC) as rn
        FROM 
            income_budgets
    )
    SELECT 
        c.name as client_name,
        s.name as service_name,
        lb.budgeted_amount,
        lb.period_year,
        lb.period_month
    FROM 
        LatestBudgets lb
    JOIN 
        clients c ON lb.client_id = c.id
    JOIN 
        services s ON lb.service_id = s.id
    WHERE 
        lb.rn = 1
    ORDER BY 
        c.name, s.name;
    """
    
    rows = await conn.fetch(query)
    
    print("| Cliente | Servicio | Monto | Periodo |")
    print("| :--- | :--- | :--- | :--- |")
    for row in rows:
        period = f"{row['period_month']}/{row['period_year']}"
        print(f"| {row['client_name']} | {row['service_name']} | {row['budgeted_amount']:,} | {period} |")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
