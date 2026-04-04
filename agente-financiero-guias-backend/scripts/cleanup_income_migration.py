
import asyncio
from sqlalchemy import select, delete
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.income_budget import IncomeBudget
from app.utils.enums import TransactionType

async def cleanup():
    async with SessionLocal() as db:
        print("Cleaning up income data using ORM...")
        
        # Delete income transactions
        tx_delete_stmt = delete(Transaction).where(Transaction.type == TransactionType.INCOME)
        await db.execute(tx_delete_stmt)
        
        # Delete all income budgets
        ib_delete_stmt = delete(IncomeBudget)
        await db.execute(ib_delete_stmt)
        
        await db.commit()
        
        # Verify
        res_tx = await db.execute(select(Transaction).where(Transaction.type == TransactionType.INCOME))
        count_tx = len(res_tx.scalars().all())
        
        res_ib = await db.execute(select(IncomeBudget))
        count_ib = len(res_ib.scalars().all())
        
        print(f"Cleanup complete.")
        print(f"Transactions (income) count: {count_tx} (Expected: 0)")
        print(f"Income Budgets count: {count_ib} (Expected: 0)")

if __name__ == "__main__":
    asyncio.run(cleanup())
