import asyncio
from app.database import SessionLocal
from app.models.commission import Commission
from sqlalchemy import select

async def dump_comms():
    async with SessionLocal() as db:
        res = await db.execute(select(Commission))
        for c in res.scalars():
            print(f"ID: {c.id} | Amount: {c.amount} | Status: {c.status}")

if __name__ == "__main__":
    asyncio.run(dump_comms())
