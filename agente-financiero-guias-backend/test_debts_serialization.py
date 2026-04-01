import asyncio
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import SessionLocal
from app.main import app
from app.models.debt import Debt, DebtInstallment
from app.schemas.debt import DebtResponse

async def main():
    company_id_str = "aeb56588-5e15-4ce2-b24b-065ebf842c44"
    print("Testing get debts...")
    async with SessionLocal() as db:
        try:
            from sqlalchemy.orm import joinedload
            query = select(Debt).options(joinedload(Debt.debt_installments)).where(Debt.company_id == company_id_str)
            res = await db.execute(query)
            debts = res.scalars().unique().all()
            print(f"Found {len(debts)} debts in DB")
            for d in debts:
                try:
                    schema = DebtResponse.model_validate(d)
                except Exception as e:
                    print(f"Validation error on debt {d.id}: {e}")
                    
        except Exception as e:
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
