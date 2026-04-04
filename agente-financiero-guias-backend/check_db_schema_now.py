import asyncio
from app.database import engine
from sqlalchemy import text

async def check_schema():
    async with engine.connect() as conn:
        print("Checking columns in 'transactions' table...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'transactions'"))
        cols = [r[0] for r in res]
        for col in cols:
            print(f"- {col}")

        print("\nChecking columns in 'income_budgets' table...")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'income_budgets'"))
        cols = [r[0] for r in res]
        for col in cols:
            print(f"- {col}")

if __name__ == "__main__":
    asyncio.run(check_schema())
