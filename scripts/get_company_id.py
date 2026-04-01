import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.transaction import Transaction

async def get_company_id():
    async with SessionLocal() as db:
        r = await db.execute(select(Transaction.company_id).limit(1))
        cid = r.scalar()
        print(f"COMPANY_ID: {cid}")

if __name__ == "__main__":
    asyncio.run(get_company_id())
