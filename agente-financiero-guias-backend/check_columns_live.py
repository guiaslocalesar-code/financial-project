
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_columns():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'clients'"))
        cols = result.fetchall()
        for col in cols:
            print(f"Column: {col[0]}, Type: {col[1]}")

if __name__ == "__main__":
    asyncio.run(check_columns())
