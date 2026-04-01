import asyncio
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models.company import Company
from app.models.expense_type import ExpenseType
from app.models.debt import Debt
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload

TARGET_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
engine = create_async_engine(TARGET_URL, echo=False)
LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def test_types():
    async with LocalSession() as db:
        company_id = UUID("aeb56588-5e15-4ce2-b24b-065ebf842c44")
        result = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company_id))
        types = result.scalars().all()
        print("ExpenseTypes found:", len(types))
        try:
            # Simulate what FastAPI does when returning dicts without a clear response_model or with a flawed one
            encoded = jsonable_encoder(types)
            print("Successfully encoded ExpenseTypes")
        except Exception as e:
            print(f"Error encoding ExpenseTypes: {e}")

async def test_debts():
    async with LocalSession() as db:
        company_id = UUID("aeb56588-5e15-4ce2-b24b-065ebf842c44")
        result = await db.execute(select(Debt).options(joinedload(Debt.debt_installments)).where(Debt.company_id == company_id))
        debts = result.scalars().all()
        print("\nDebts found:", len(debts))
        try:
            encoded = jsonable_encoder(debts)
            print("Successfully encoded Debts")
        except Exception as e:
            print(f"Error encoding Debts: {e}")

if __name__ == "__main__":
    asyncio.run(test_types())
    asyncio.run(test_debts())
