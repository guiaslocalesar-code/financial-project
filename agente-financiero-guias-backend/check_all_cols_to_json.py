
import asyncio
import json
from sqlalchemy import text
from app.database import SessionLocal

async def check_all_columns():
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        out = {}
        for table in tables:
            res = await db.execute(text(f"SELECT * FROM {table} LIMIT 0"))
            out[table] = list(res.keys())
        
        with open('current_db_schema.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2)
        print("Schema saved to current_db_schema.json")

if __name__ == "__main__":
    asyncio.run(check_all_columns())
