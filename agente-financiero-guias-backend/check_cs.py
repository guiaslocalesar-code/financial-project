import asyncio
from sqlalchemy import select, text
from app.database import SessionLocal, engine
from app.models.client_service import ClientService

async def check_data():
    async with SessionLocal() as db:
        print("--- CLIENT_SERVICES ---")
        result = await db.execute(select(ClientService).limit(10))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, ClientID: {row.client_id}, ServiceID: {row.service_id}, Fee: {row.monthly_fee}, Currency: {row.currency}")

if __name__ == "__main__":
    asyncio.run(check_data())
