import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.commission import Commission

async def check():
    async with SessionLocal() as db:
        # The ID from the screenshot looks like ce4d8b97-d6b8-4d9b-859a-58c38865184f
        # Let's search for partial to be sure
        print("Searching for commission...")
        res = await db.execute(select(Commission))
        comms = res.scalars().all()
        for c in comms:
            id_str = str(c.id)
            if "ce4d8b97" in id_str or "58c38865" in id_str:
                print(f"FOUND: ID={c.id}, Status={c.status}, Amount={c.amount}")
                return
        print("Commission NOT FOUND in DB.")

if __name__ == '__main__':
    asyncio.run(check())
