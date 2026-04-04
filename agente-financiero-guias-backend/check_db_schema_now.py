import asyncio
import uuid
from app.database import engine
from sqlalchemy import text

async def check_schema():
    async with engine.connect() as conn:
        print("Checking tables in database...")
        tables = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        print("Tables:", [r[0] for r in tables])
        
        print("\nChecking columns in 'transactions' table...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'transactions'"))
        print("Transactions columns:", [r[0] for r in res])

        print("\nChecking columns in 'income_budgets' table...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'income_budgets'"))
        print("Income Budgets columns:", [r[0] for r in res])

if __name__ == "__main__":
    asyncio.run(check_schema())
