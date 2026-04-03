import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        print("Payment methods rows:")
        res = await db.execute(text("SELECT id, name, type FROM payment_methods"))
        for r in res.fetchall():
            print(r[0], r[1], repr(r[2]))

if __name__ == "__main__":
    asyncio.run(check())
