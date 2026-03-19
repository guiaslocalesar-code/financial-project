import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def explore():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        print('--- SCHEMAS ---')
        res = await conn.execute(text('SELECT schema_name FROM information_schema.schemata;'))
        for r in res:
            print(r[0])
            
        print('\n--- ALL TABLES ---')
        res = await conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog') 
            ORDER BY table_schema, table_name;
        """))
        tables = res.fetchall()
        for t in tables:
            schema, name = t[0], t[1]
            try:
                count_res = await conn.execute(text(f'SELECT count(*) FROM "{schema}"."{name}"'))
                count = count_res.scalar()
                print(f'{schema}.{name}: {count} rows')
            except Exception as e:
                print(f'{schema}.{name}: Error reading count - {e}')

if __name__ == "__main__":
    asyncio.run(explore())
