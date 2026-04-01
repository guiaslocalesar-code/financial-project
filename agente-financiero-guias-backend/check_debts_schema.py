import asyncio
import json
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'debts'"))
        debts = [{'name': r[0], 'type': r[1]} for r in res]
        res2 = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'debt_installments'"))
        instals = [{'name': r[0], 'type': r[1]} for r in res2]
        with open("debts_schema.json", "w") as f:
            json.dump({"debts": debts, "debt_installments": instals}, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
