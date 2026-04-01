import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.payment_method import PaymentMethod

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(PaymentMethod))
        pms = res.scalars().all()
        with open("pm_utf8.txt", "w", encoding="utf-8") as f:
            for pm in pms:
                f.write(f"ID: {pm.id}, Name: {pm.name}, Type: {pm.type}\n")

if __name__ == "__main__":
    asyncio.run(main())
