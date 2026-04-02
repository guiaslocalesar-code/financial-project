import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM commissions LIMIT 1"))
        row = res.fetchone()
        if row:
            print(f"ROW:{dict(row._mapping)}")
        else:
            print("EMPTY_TABLE")

if __name__ == "__main__":
    asyncio.run(check())
