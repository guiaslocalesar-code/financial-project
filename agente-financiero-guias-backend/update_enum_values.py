import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    print("Normalizing db enum values to UPPERCASE...")
    async with SessionLocal() as db:
        await db.execute(text("UPDATE debts SET status = UPPER(status)"))
        await db.execute(text("UPDATE debt_installments SET status = UPPER(status)"))
        await db.execute(text("UPDATE debts SET interest_type = UPPER(interest_type) WHERE interest_type IS NOT NULL"))
        await db.commit()
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
