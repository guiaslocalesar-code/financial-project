import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def get_version():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        try:
            res = await conn.execute(text('SELECT version_num FROM alembic_version'))
            v = res.scalar()
            print(f"VERSION:{v}")
        except Exception as e:
            print(f"ERROR:{e}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(get_version())
