
import asyncio
import json
from sqlalchemy import text
from app.database import SessionLocal

async def get_companies():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT id, name FROM companies"))
        companies = [{"id": str(row[0]), "name": row[1]} for row in res]
        print(json.dumps(companies, indent=2))

if __name__ == "__main__":
    asyncio.run(get_companies())
