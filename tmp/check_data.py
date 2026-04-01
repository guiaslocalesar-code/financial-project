import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_data():
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(database_url)
    
    print("Checking CLIENT_SERVICES:")
    count_cs = await conn.fetchval("SELECT count(*) FROM client_services")
    non_zero_cs = await conn.fetchval("SELECT count(*) FROM client_services WHERE monthly_fee > 0")
    print(f"Total rows: {count_cs}, Non-zero monthly_fee: {non_zero_cs}")
    
    print("\nChecking INCOME_BUDGETS:")
    count_ib = await conn.fetchval("SELECT count(*) FROM income_budgets")
    non_zero_ib = await conn.fetchval("SELECT count(*) FROM income_budgets WHERE budgeted_amount > 0")
    print(f"Total rows: {count_ib}, Non-zero budgeted_amount: {non_zero_ib}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_data())
