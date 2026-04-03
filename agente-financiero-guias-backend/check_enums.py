import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        print("PaymentMethodType enum values:")
        res1 = await db.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'paymentmethodtype'::regtype"))
        print([r[0] for r in res1.fetchall()])
        
        print("PaymentMethod (transaction) enum values:")
        try:
            res2 = await db.execute(text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'paymentmethod'::regtype"))
            print([r[0] for r in res2.fetchall()])
        except Exception as e:
            print("Could not fetch paymentmethod enum:", str(e))

if __name__ == "__main__":
    asyncio.run(check())
