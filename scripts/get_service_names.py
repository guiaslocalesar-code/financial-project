import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.service import Service

async def get_service_names():
    ids = ['45311', '45413', '45612', '45892', '45897', '45900']
    async with SessionLocal() as db:
        r = await db.execute(select(Service.id, Service.name).where(Service.id.in_(ids)))
        for row in r.all():
            print(f"{row.id} | {row.name}")

if __name__ == "__main__":
    asyncio.run(get_service_names())
