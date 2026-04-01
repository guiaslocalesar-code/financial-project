import asyncio
import json
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'commission_rules'"))
        cols = [{'name': r[0], 'type': r[1]} for r in res]
        print(json.dumps(cols, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
