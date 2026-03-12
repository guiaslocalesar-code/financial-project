
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def check():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'clients' AND column_name = 'id'"))
        print(f"Clients ID type: {res.all()}")
        
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'services' AND column_name = 'id'"))
        print(f"Services ID type: {res.all()}")
        
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'companies' AND column_name = 'id'"))
        print(f"Companies ID type: {res.all()}")
        
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'transactions' AND column_name = 'id'"))
        print(f"Transactions ID type: {res.all()}")
        
        res = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'income_budgets' AND column_name = 'id'"))
        print(f"Income Budgets ID type: {res.all()}")
        
        res = await db.execute(text("SELECT id, name FROM clients LIMIT 5"))
        print(f"Clients sample: {res.all()}")

        res = await db.execute(text("SELECT id, name FROM clients WHERE name ILIKE '%Autocentro%' OR name ILIKE '%Venzo%'"))
        print(f"Specific Clients: {res.all()}")

if __name__ == "__main__":
    asyncio.run(check())
