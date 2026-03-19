import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.service import Service
from app.models.client import Client

async def check_data():
    async with SessionLocal() as db:
        print("--- SERVICES ---")
        result = await db.execute(select(Service).limit(10))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, Name: {row.name}")
        
        print("\n--- CLIENTS ---")
        result = await db.execute(select(Client).limit(10))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, Name: {row.name}")

if __name__ == "__main__":
    asyncio.run(check_data())
