
import asyncio
import json
import os
from sqlalchemy import text
from app.database import SessionLocal

async def check_all():
    summary = {}
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        for table in tables:
            count_res = await db.execute(text(f"SELECT count(*) FROM {table}"))
            count = count_res.scalar()
            
            col_res = await db.execute(text(f"SELECT * FROM {table} LIMIT 0"))
            columns = list(col_res.keys())
            
            summary[table] = {
                "count": count,
                "columns": columns
            }
            
    with open('db_status_report.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    asyncio.run(check_all())
