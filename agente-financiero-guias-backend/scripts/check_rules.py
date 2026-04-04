import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule

async def check():
    async with SessionLocal() as db:
        r1 = await db.execute(select(func.count(CommissionRecipient.id)))
        print(f"Total recipients: {r1.scalar()}")
        
        r2 = await db.execute(select(func.count(CommissionRule.id)))
        print(f"Total rules: {r2.scalar()}")
        
        if r2.scalar() > 0:
            r3 = await db.execute(select(CommissionRule, CommissionRecipient.name).join(CommissionRecipient).limit(10))
            for rule, name in r3:
                print(f"Recipient: {name} | Client: {rule.client_id} | Service: {rule.service_id} | %: {rule.percentage}")

if __name__ == "__main__":
    asyncio.run(check())
