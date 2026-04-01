import asyncio
import asyncpg
import sys

async def try_connect():
    passwords = [
        "FinancialAgent_2026!",
        "FinancialAgent_2026",
    ]
    
    for pwd in passwords:
        dsn = f"postgresql://postgres:{pwd}@db.fumejzkghviszmyfjegg.supabase.co:5432/postgres"
        try:
            print(f"Trying password: {pwd}...")
            conn = await asyncpg.connect(dsn, timeout=5)
            print("SUCCESS! Password is:", pwd)
            await conn.close()
            with open("tmp/supabase_dsn.txt", "w") as f:
                f.write(dsn)
            return
        except Exception as e:
            print(f"Failed with {pwd}: {e}")

if __name__ == "__main__":
    asyncio.run(try_connect())
