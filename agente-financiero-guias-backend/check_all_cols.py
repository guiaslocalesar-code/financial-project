
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_all_columns():
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        for table in tables:
            res = await db.execute(text(f"SELECT * FROM {table} LIMIT 1"))
            print(f"Table: {table} | Columns: {list(res.keys())}")

if __name__ == "__main__":
    asyncio.run(check_all_columns())
