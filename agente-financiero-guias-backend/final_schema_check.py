import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'commissions'"))
        cols = [r[0] for r in res.fetchall()]
        print(f"MY_COLS:{cols}")

if __name__ == "__main__":
    asyncio.run(check())
