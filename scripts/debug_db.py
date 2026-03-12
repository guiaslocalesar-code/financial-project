import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        try:
            # List tables
            res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            print("Tables in DB:")
            for row in res:
                print(f"- {row[0]}")
            
            # Count transactions
            res = await db.execute(text("SELECT count(*) FROM transactions"))
            print(f"\nTotal transactions: {res.scalar()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
