import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.transaction import Transaction

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Transaction.payment_method).limit(5))
        vals = res.scalars().all()
        print(f"Values: {vals}")

if __name__ == "__main__":
    asyncio.run(check())
