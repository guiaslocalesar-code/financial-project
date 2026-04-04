import asyncio
from sqlalchemy import text
from app.database import engine

async def check():
    print('Checking columns in commissions table...')
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'commissions'"))
        for r in res:
            print(f"- {r[0]}")

if __name__ == "__main__":
    asyncio.run(check())
