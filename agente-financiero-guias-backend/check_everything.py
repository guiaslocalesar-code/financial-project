import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_all():
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        for table in tables:
            print(f"\n--- TABLE: {table} ---")
            res = await db.execute(text(f"SELECT * FROM {table} LIMIT 1"))
            print(f"Columns: {res.keys()}")
            row = res.fetchone()
            if row:
                # Limit to first 100 chars of each value to avoid truncation
                print(f"Sample: { {k: str(v)[:100] for k, v in zip(res.keys(), row)} }")

if __name__ == "__main__":
    asyncio.run(check_all())
