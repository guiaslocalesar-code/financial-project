import asyncio
from app.database import SessionLocal
from app.models.company import Company
from sqlalchemy import select

async def get_company():
    async with SessionLocal() as db:
        result = await db.execute(select(Company).limit(1))
        company = result.scalar()
        if company:
            print(company.id)
        else:
            print("No company found")

if __name__ == "__main__":
    asyncio.run(get_company())
