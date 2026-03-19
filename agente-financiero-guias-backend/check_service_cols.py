import asyncio
from sqlalchemy import select, text
from app.database import SessionLocal, engine

async def check_columns():
    async with SessionLocal() as db:
        print("--- SERVICE COLUMNS ---")
        result = await db.execute(text("SELECT * FROM services LIMIT 1"))
        print(f"Columns: {result.keys()}")
        row = result.fetchone()
        if row:
            print(f"Example Row: {dict(row._mapping)}")

if __name__ == "__main__":
    asyncio.run(check_columns())
