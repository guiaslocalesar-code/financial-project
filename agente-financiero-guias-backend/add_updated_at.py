import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        print("Adding updated_at to debt_installments...")
        await db.execute(text("ALTER TABLE debt_installments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
        await db.commit()
        print("Done")

if __name__ == "__main__":
    asyncio.run(main())
