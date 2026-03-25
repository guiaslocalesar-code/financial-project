import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def inspect_db():
    url = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:GuiasSA2020%40@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    print(f"Connecting to: {url}")
    engine = create_async_engine(url)
    
    async with engine.connect() as conn:
        # Get table names
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in res]
        print(f"Tables found: {tables}")
        
        for table in tables:
            print(f"\nColumns for '{table}':")
            res = await conn.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'"))
            for col in res:
                print(f" - {col[0]} ({col[1]}, nullable={col[2]})")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect_db())
