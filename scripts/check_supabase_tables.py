import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

SUPABASE_URL = "postgresql+asyncpg://postgres.fumejzkghviszmyfjegg:Finanzas2025!@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
REQUIRED = ["companies","clients","services","client_services","expense_types","expense_categories","expense_budgets","income_budgets","invoices","invoice_items","transactions","payment_methods","commissions","commission_recipients","commission_rules","debts","debt_installments","users","user_companies"]

async def main():
    engine = create_async_engine(SUPABASE_URL, echo=False)
    async with engine.connect() as conn:
        r = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
        existing = [row[0] for row in r.fetchall()]
        print("EXISTING:", existing)
        missing = [t for t in REQUIRED if t not in existing]
        print("MISSING:", missing)
        if "transactions" in existing:
            r2 = await conn.execute(text("SELECT DISTINCT payment_method FROM transactions WHERE payment_method IS NOT NULL LIMIT 20"))
            vals = [row[0] for row in r2.fetchall()]
            print("PAYMENT_METHODS:", vals)
        if "commissions" in existing:
            r3 = await conn.execute(text("SELECT count(*) FROM commissions"))
            print("COMMISSIONS_COUNT:", r3.scalar())
        if "debts" in existing:
            r4 = await conn.execute(text("SELECT count(*) FROM debts"))
            print("DEBTS_COUNT:", r4.scalar())
    await engine.dispose()

asyncio.run(main())
