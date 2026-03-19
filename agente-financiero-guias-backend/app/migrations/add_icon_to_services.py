import asyncio
from sqlalchemy import text
from app.database import engine

async def migrate():
    async with engine.begin() as conn:
        print("Checking if 'icon' column exists in 'services' table...")
        # Check if column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='services' AND column_name='icon';
        """))
        
        if not result.fetchone():
            print("Adding 'icon' column...")
            await conn.execute(text("ALTER TABLE services ADD COLUMN icon VARCHAR(50);"))
            print("Migration successful.")
        else:
            print("'icon' column already exists.")

if __name__ == "__main__":
    asyncio.run(migrate())
