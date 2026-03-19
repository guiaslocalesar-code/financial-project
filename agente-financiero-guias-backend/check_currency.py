import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.transaction import Transaction

async def check_data():
    async with SessionLocal() as db:
        from app.utils.enums import TransactionType
        result = await db.execute(select(Transaction).where(Transaction.type == TransactionType.INCOME).limit(5))
        txs = result.scalars().all()
        for tx in txs:
            print(f"ID: {tx.id}, Amount: {tx.amount}, Currency: {tx.currency}, ServiceID: {tx.service_id}")

if __name__ == "__main__":
    asyncio.run(check_data())
