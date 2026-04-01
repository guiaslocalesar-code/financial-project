import asyncio
from sqlalchemy import select
from app.database import SessionLocal
from app.models.expense_type import ExpenseType

async def get_sueldos_id():
    async with SessionLocal() as db:
        query = select(ExpenseType.id, ExpenseType.name)
        result = await db.execute(query)
        for row in result.all():
            print(f"ID: {row.id} | Name: {row.name}")

if __name__ == "__main__":
    asyncio.run(get_sueldos_id())
