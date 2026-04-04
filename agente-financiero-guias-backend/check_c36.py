import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT id, name, imagen FROM clients WHERE id='c36'"))
        row = res.fetchone()
        print(row)

if __name__ == "__main__":
    asyncio.run(check())
