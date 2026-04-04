import asyncio
from app.database import SessionLocal
from app.models.commission import Commission
from sqlalchemy import select

async def search():
    async with SessionLocal() as db:
        res = await db.execute(select(Commission.id, Commission.status))
        for row in res.fetchall():
            id_str = str(row[0])
            if "55f0" in id_str or "d37885" in id_str or "64d3" in id_str or "d4d7" in id_str:
                print("MATCH:", id_str, row[1])

if __name__ == "__main__":
    asyncio.run(search())
