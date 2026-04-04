import asyncio
from app.database import SessionLocal
from app.models.commission import Commission
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.transaction import Transaction
from app.models.client import Client

async def search_quiro():
    async with SessionLocal() as db:
        res = await db.execute(select(Commission).options(
            joinedload(Commission.transaction).joinedload(Transaction.client)
        ))
        for c in res.scalars():
            if c.transaction and c.transaction.client and "quiro" in c.transaction.client.name.lower():
                print(c.id, c.status)

if __name__ == "__main__":
    asyncio.run(search_quiro())
