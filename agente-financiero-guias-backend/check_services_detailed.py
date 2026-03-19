import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_all():
    async with SessionLocal() as db:
        print("--- SERVICES DETAILED ---")
        result = await db.execute(text("SELECT * FROM services LIMIT 5"))
        keys = result.keys()
        for row in result:
            print({k: v for k, v in zip(keys, row)})

if __name__ == "__main__":
    asyncio.run(check_all())
