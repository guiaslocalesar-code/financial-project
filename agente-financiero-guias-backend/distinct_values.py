import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT DISTINCT status FROM debts"))
        res2 = await db.execute(text("SELECT DISTINCT status FROM debt_installments"))
        res3 = await db.execute(text("SELECT DISTINCT interest_type FROM debts"))
        out = {
            "debts.status": [r[0] for r in res],
            "debt_installments.status": [r[0] for r in res2],
            "debts.interest_type": [r[0] for r in res3]
        }
        import json
        with open("distinct.json", "w") as f:
            json.dump(out, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
