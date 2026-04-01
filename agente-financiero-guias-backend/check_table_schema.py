import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        tables = ["commission_recipients", "commission_rules", "commissions"]
        for t in tables:
            print(f"--- Table: {t} ---")
            res = await db.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'"))
            for row in res:
                print(f"  {row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(main())
