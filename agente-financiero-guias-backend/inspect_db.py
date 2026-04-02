import asyncio
from sqlalchemy import text
import sys
import os

# Ensure backend folder is in sys.path
sys.path.append(os.getcwd())

from app.database import engine

async def inspect():
    async with engine.connect() as conn:
        print("--- TABLES IN PUBLIC SCHEMA ---")
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in res.fetchall()]
        print(f"Tables: {tables}")
        
        for t in ['users', 'company_users', 'profiles', 'roles', 'user_roles', 'commissions']:
            if t in tables:
                print(f"--- COLUMNS IN {t} ---")
                res = await conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{t}'"))
                cols = [f"- {r[0]} ({r[1]})" for r in res.fetchall()]
                print("\n".join(cols))
                
        print("--- TABLES IN AUTH SCHEMA ---")
        try:
            res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='auth'"))
            auth_tables = [r[0] for r in res.fetchall()]
            print(f"Auth Tables: {auth_tables}")
            if 'users' in auth_tables:
                print("--- COLUMNS IN auth.users ---")
                res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='auth' AND table_name='users'"))
                cols = [f"- {r[0]} ({r[1]})" for r in res.fetchall()]
                print("\n".join(cols))
        except Exception as e:
            print(f"Could not read auth schema: {e}")

asyncio.run(inspect())
