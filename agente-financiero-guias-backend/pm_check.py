import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'payment_methods'"))
        cols = [(r[0], r[1]) for r in res.fetchall()]
        print(f"PAYMENT_METHODS_COLS: {cols}")

if __name__ == "__main__":
    asyncio.run(check())
