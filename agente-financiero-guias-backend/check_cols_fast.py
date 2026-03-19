
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_columns():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT * FROM companies LIMIT 1"))
        print(f"Companies Columns: {res.keys()}")
        
        res = await db.execute(text("SELECT * FROM clients LIMIT 1"))
        print(f"Clients Columns: {res.keys()}")

if __name__ == "__main__":
    asyncio.run(check_columns())
