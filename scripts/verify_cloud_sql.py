import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.transaction import Transaction

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Transaction.id, Transaction.payment_method, Transaction.payment_method_id).limit(10))
        rows = res.all()
        for r in rows:
            print(f"ID: {r.id}, PM: {r.payment_method}, PM_ID: {r.payment_method_id}")

if __name__ == "__main__":
    asyncio.run(check())
