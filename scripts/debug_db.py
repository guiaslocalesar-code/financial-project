import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.database import SessionLocal
from sqlalchemy import select
from app.models.client import Client

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(Client).where(Client.id.in_(['c23', 'c14', 'c36', 'C36', 'c4', 'c3'])))
        clients = res.scalars().all()
        for c in clients:
            print(f"Found: {c.id} - {c.company_id}")

if __name__ == "__main__":
    asyncio.run(main())
