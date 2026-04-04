import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.commission import Commission

async def check():
    async with SessionLocal() as db:
        r = await db.execute(select(func.count(Commission.id)))
        count = r.scalar()
        print(f"Total commissions in DB: {count}")
        
        if count > 0:
            # Check first 5
            r2 = await db.execute(select(Commission).limit(5))
            for c in r2.scalars():
                print(f"ID: {c.id} | Amount: {c.commission_amount} | Status: {c.status}")

if __name__ == "__main__":
    asyncio.run(check())
