import asyncio
from sqlalchemy import select, text
from app.database import SessionLocal
from app.models.commission import Commission

async def diagnose():
    async with SessionLocal() as db:
        id_to_check = "a543f9c3-bdb8-494b-866e-910ca6a709c3"
        print(f"--- Diagnosing commission {id_to_check} ---")
        
        # 1. Get the commission row
        res = await db.execute(select(Commission).where(Commission.id == id_to_check))
        comm = res.scalar_one_or_none()
        
        if not comm:
            print("Commission NOT FOUND.")
            return

        print(f"ID: {comm.id}")
        print(f"Status: {comm.status}")
        print(f"Transaction ID: {comm.transaction_id}")
        print(f"Amount: {comm.amount}")
        print(f"Payment Transaction ID: {comm.payment_transaction_id}")
        print(f"Updated At: {comm.updated_at}")
        
        # 2. Check for other commissions linked to the SAME INCOME TRANSACTION
        print(f"\n--- Checking for duplicates for Transaction {comm.transaction_id} ---")
        res2 = await db.execute(select(Commission).where(Commission.transaction_id == comm.transaction_id))
        all_comms = res2.scalars().all()
        print(f"Found {len(all_comms)} commissions for this transaction:")
        for c in all_comms:
            print(f"  - ID: {c.id}, Status: {c.status}, Amount: {c.amount}, Recipient: {c.recipient_id}")

if __name__ == '__main__':
    asyncio.run(diagnose())
