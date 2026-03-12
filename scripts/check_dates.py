import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT type, MIN(transaction_date), MAX(transaction_date) FROM transactions GROUP BY type"))
        for row in res:
            print(f"Type: {row[0]}, Min: {row[1]}, Max: {row[2]}")

if __name__ == "__main__":
    asyncio.run(check())
