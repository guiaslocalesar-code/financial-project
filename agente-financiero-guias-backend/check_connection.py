import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def test():
    async with SessionLocal() as db:
        try:
            res = await db.execute(text("SELECT current_database(), current_user, version()"))
            row = res.first()
            print("DB:", row[0])
            print("User:", row[1])
            print("Version:", row[2][:60])
            
            tables_res = await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
            tables = [r[0] for r in tables_res]
            print("\nTablas en produccion:")
            for t in tables:
                print(" -", t)
        except Exception as e:
            import traceback
            print("Error:", e)
            traceback.print_exc()

asyncio.run(test())
