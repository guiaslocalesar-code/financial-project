import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.client_service import ClientService

async def check_data():
    async with SessionLocal() as db:
        print("--- CLIENT_SERVICES (Non-ARS Currency) ---")
        result = await db.execute(select(ClientService).where(ClientService.currency != 'ARS'))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, ServiceID: {row.service_id}, Fee: {row.monthly_fee}, Currency: {row.currency}")
        if not rows:
            print("No rows found with Currency != 'ARS'")

if __name__ == "__main__":
    asyncio.run(check_data())
