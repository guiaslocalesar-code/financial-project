import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def fix_db():
    async with SessionLocal() as db:
        print("Running SQL...")
        await db.execute(text("ALTER TABLE payment_methods ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
        await db.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(fix_db())
