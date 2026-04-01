import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app.config import settings

# Import the models so they are registered in the Base metadata
from app.models.debt import Debt, DebtInstallment

TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"

async def create_tables():
    engine = create_async_engine(TARGET_URL, echo=True)
    async with engine.begin() as conn:
        print("Creating debts tables in Supabase...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(create_tables())
