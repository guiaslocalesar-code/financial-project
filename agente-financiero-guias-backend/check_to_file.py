import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_all():
    async with SessionLocal() as db:
        with open("db_summary.txt", "w", encoding="utf-8") as f:
            result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            for table in tables:
                f.write(f"\n--- TABLE: {table} ---\n")
                res = await db.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                f.write(f"Columns: {', '.join(res.keys())}\n")
                row = res.fetchone()
                if row:
                    data = {k: str(v) for k, v in zip(res.keys(), row)}
                    f.write(f"Sample: {data}\n")

if __name__ == "__main__":
    asyncio.run(check_all())
