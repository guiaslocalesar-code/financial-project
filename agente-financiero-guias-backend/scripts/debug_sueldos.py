import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.expense_budget import ExpenseBudget
from app.models.expense_type import ExpenseType

async def debug_sueldos():
    async with SessionLocal() as db:
        # Check all budgets for March 2026
        query = select(
            ExpenseType.name,
            ExpenseBudget.description,
            ExpenseBudget.budgeted_amount,
            ExpenseBudget.expense_type_id
        ).join(ExpenseType).where(
            ExpenseBudget.period_month == 3,
            ExpenseBudget.period_year == 2026,
            ExpenseType.name.ilike("%sueldo%")
        )
        
        result = await db.execute(query)
        rows = result.all()
        print(f"Total budget records for March 2026: {len(rows)}")
        for r in rows:
            print(f"Category: {r.name} | Desc: {r.description} | Amt: {r.budgeted_amount} | TypeID: {r.expense_type_id}")

if __name__ == "__main__":
    asyncio.run(debug_sueldos())
