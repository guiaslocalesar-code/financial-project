import asyncio
import json
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        tables = ["commission_recipients", "commission_rules", "commissions"]
        schema = {}
        for t in tables:
            res = await db.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'"))
            schema[t] = [{'name': row[0], 'type': row[1]} for row in res]
        with open("schema_dump.json", "w") as f:
            json.dump(schema, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
