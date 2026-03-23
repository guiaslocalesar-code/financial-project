import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def test_connect():
    print(f"Connecting to: {settings.async_database_url}")
    try:
        engine = create_async_engine(settings.async_database_url)
        async with engine.connect() as conn:
            print("Successfully connected!")
        await engine.dispose()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
