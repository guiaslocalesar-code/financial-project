import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.invoice_item import InvoiceItem

async def check_data():
    async with SessionLocal() as db:
        print("--- INVOICE_ITEMS ---")
        result = await db.execute(select(InvoiceItem).limit(10))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, ServiceID: {row.service_id}, UnitPrice: {row.unit_price}, Subtotal: {row.subtotal}")

if __name__ == "__main__":
    asyncio.run(check_data())
