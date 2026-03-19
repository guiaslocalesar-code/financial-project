import asyncio
from sqlalchemy import select
from app.database import SessionLocal, engine
from app.models.income_budget import IncomeBudget

async def check_data():
    async with SessionLocal() as db:
        print("--- INCOME_BUDGETS ---")
        result = await db.execute(select(IncomeBudget).limit(10))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, Budgeted: {row.budgeted_amount}, Actual: {row.actual_amount}, ServiceID: {row.service_id}")

if __name__ == "__main__":
    asyncio.run(check_data())
