import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def add_column():
    # Use the URL from settings
    url = settings.async_database_url
    print(f"Connecting to: {url}")
    
    engine = create_async_engine(url)
    
    try:
        async with engine.begin() as conn:
            print("Adding payment_method_id column to transactions table...")
            await conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_method_id UUID REFERENCES payment_methods(id)"))
            print("Column added successfully or already exists.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_column())
