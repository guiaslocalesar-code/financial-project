import asyncio
import datetime
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction

async def main():
    async with SessionLocal() as db:
        res1 = await db.execute(select(func.count(ExpenseBudget.id)).where(ExpenseBudget.period_year >= 2026))
        budgets_count = res1.scalar()
        
        res2 = await db.execute(select(func.count(Transaction.id)).where(Transaction.type == 'expense', Transaction.transaction_date >= datetime.date(2026, 1, 1)))
        transactions_count = res2.scalar()
        
        print(f"Cloud SQL - Budgets 2026: {budgets_count}")
        print(f"Cloud SQL - Transactions (Expense) 2026: {transactions_count}")

if __name__ == "__main__":
    asyncio.run(main())
