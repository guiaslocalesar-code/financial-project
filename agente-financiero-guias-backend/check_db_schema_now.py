import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        # Check commissions
        res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'commissions'"))
        print("commissions:", [r[0] for r in res.fetchall()])
        
        # Check transactions
        res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'transactions'"))
        print("transactions:", [r[0] for r in res.fetchall()])

        # Check income_budgets
        res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'income_budgets'"))
        print("income_budgets:", [r[0] for r in res.fetchall()])

        # Also get Electro Alem commission to see why it fails PAY
        comm_id = "c60d060e-645c-47d1-8bbb-2234422feff7"
        res = await db.execute(text(f"SELECT id, status, commission_amount FROM commissions WHERE id = '{comm_id}'"))
        print("Electro Alem Comm:", res.fetchone())

if __name__ == "__main__":
    asyncio.run(check())
