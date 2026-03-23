import asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def inspect_db():
    print(f"Inspecting DB: {settings.async_database_url}")
    engine = create_async_engine(settings.async_database_url)
    
    try:
        async with engine.connect() as conn:
            print("Connected! Inspecting tables...")
            # Unfortunately, inspect() is typically synchronous. 
            # We can use it with run_sync.
            def get_tables(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_tables)
            print(f"Tables: {tables}")
            
            if "transactions" in tables:
                def get_cols(connection):
                    inspector = inspect(connection)
                    return [c['name'] for c in inspector.get_columns("transactions")]
                cols = await conn.run_sync(get_cols)
                print(f"Columns in 'transactions': {cols}")
    except Exception as e:
        print(f"Error during inspection: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect_db())
