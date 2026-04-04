import asyncio
from app.database import SessionLocal
from app.models.commission import Commission
from sqlalchemy import select

async def check():
    async with SessionLocal() as db:
        id_to_check = "a543f9c3-bdb8-494b-866e-910ca6a709c3"
        print(f"Checking commission {id_to_check}...")
        res = await db.execute(select(Commission).where(Commission.id == id_to_check))
        comm = res.scalar_one_or_none()
        if comm:
            print(f"Status in DB: {comm.status} (Type: {type(comm.status)})")
            print(f"Payment Transaction ID: {comm.payment_transaction_id}")
        else:
            print("Commission NOT FOUND")

if __name__ == '__main__':
    asyncio.run(check())
