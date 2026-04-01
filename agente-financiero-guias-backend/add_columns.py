import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        for t in ["commission_recipients", "commission_rules", "commissions"]:
            print(f"Adding updated_at to {t}...")
            try:
                await db.execute(text(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
                await db.commit()
                print("Success")
            except Exception as e:
                print(f"Error {t}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
