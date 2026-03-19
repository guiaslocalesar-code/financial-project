
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check_tables():
    output = []
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        for table in tables:
            table_name = table[0]
            res_col = await session.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"))
            cols = [c[0] for c in res_col.fetchall()]
            output.append(f"Table: {table_name}\n  Columns: {', '.join(cols)}")
    
    with open("db_schema_output.txt", "w") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    asyncio.run(check_tables())
