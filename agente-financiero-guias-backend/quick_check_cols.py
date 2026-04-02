import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'commissions'"))
        cols = [r[0] for r in res.fetchall()]
        print(f"COMMISSIONS_COLUMNS:{cols}")

if __name__ == "__main__":
    asyncio.run(check())
