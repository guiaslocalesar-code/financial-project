import asyncio
from app.database import SessionLocal
from app.models.payment_method import PaymentMethod
from sqlalchemy import select

async def check():
    async with SessionLocal() as db:
        try:
            print("Fetching payment methods...")
            result = await db.execute(select(PaymentMethod).limit(1))
            pm = result.scalar_one_or_none()
            print("Success!", pm.id if pm else None)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check())
