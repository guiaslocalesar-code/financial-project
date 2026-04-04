import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.commission import Commission
from app.models.transaction import Transaction
from app.models.client import Client
from sqlalchemy.orm import joinedload

async def find_it():
    async with SessionLocal() as db:
        print("Searching for commission with amount 54000...")
        query = select(Commission).options(
            joinedload(Commission.transaction).joinedload(Transaction.client)
        ).where(Commission.amount == 54000)
        res = await db.execute(query)
        comms = res.scalars().all()
        for c in comms:
            client_name = "N/A"
            if c.transaction and c.transaction.client:
                client_name = c.transaction.client.name
            print(f"ID: {c.id}, Client: {client_name}, Status: {c.status}")

if __name__ == '__main__':
    asyncio.run(find_it())
