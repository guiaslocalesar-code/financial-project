import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("""
            SELECT et.name, count(*) 
            FROM transactions t
            JOIN expense_types et ON t.expense_type_id = et.id
            WHERE t.transaction_date >= '2026-01-01'
            GROUP BY et.name
        """))
        print("Expense types for 2026:")
        for row in res:
            print(f"- {row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
