
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def fetch_one_client():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT * FROM clients LIMIT 1"))
        client = result.fetchone()
        if client:
            print(dict(client._mapping))
        else:
            print("No clients found.")

if __name__ == "__main__":
    asyncio.run(fetch_one_client())
