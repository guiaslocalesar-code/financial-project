import asyncio
from app.database import SessionLocal
from app.models.commission import Commission
from sqlalchemy import select

async def get_ids():
    async with SessionLocal() as db:
        res = await db.execute(select(Commission.id, Commission.status))
        for row in res.fetchall():
            print(row[0], row[1])

if __name__ == "__main__":
    asyncio.run(get_ids())
