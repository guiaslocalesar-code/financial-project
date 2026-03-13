import asyncio
from app.database import engine
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT version_num FROM alembic_version'))
            current_version = result.scalar()
            print(f'Current version in DB: {current_version}')
            
            await conn.execute(text("UPDATE alembic_version SET version_num = '86444c077bf3'"))
            print('Updated alembic_version to 86444c077bf3')
    except Exception as e:
        print(f'Error: {e}')
        
if __name__ == "__main__":
    asyncio.run(main())
