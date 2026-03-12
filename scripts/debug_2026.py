import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("""
            SELECT transaction_date, amount, description, expense_type_id
            FROM transactions 
            WHERE type = 'EXPENSE'
            AND transaction_date >= '2026-01-01'
            LIMIT 10
        """))
        print("Expenses in 2026:")
        for row in res:
            print(f"- {row[0]}: ${row[1]} | {row[2]} | TypeID: {row[3]}")

if __name__ == "__main__":
    asyncio.run(check())
