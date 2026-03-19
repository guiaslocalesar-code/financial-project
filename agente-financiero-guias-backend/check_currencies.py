import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_all():
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT currency, count(*) FROM transactions GROUP BY currency"))
        for row in result:
            print(f"Currency: {row[0]}, Count: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check_all())
