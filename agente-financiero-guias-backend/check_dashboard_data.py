import asyncio
from sqlalchemy import text
from app.database import SessionLocal
from uuid import UUID

async def check_data():
    company_id = "aeb56588-5e15-4ce2-b24b-065ebf842c44"
    async with SessionLocal() as db:
        print(f"Checking data for company: {company_id}\n")
        
        # Check Debts
        try:
            res = await db.execute(text(f"SELECT COUNT(*) FROM debts WHERE company_id = '{company_id}'"))
            count = res.scalar()
            print(f"Debts count: {count}")
            if count > 0:
                res = await db.execute(text(f"SELECT * FROM debts WHERE company_id = '{company_id}' LIMIT 2"))
                for row in res.mappings():
                    print(f" - Debt: {dict(row)}")
        except Exception as e:
            print(f"Error checking debts: {e}")

        # Check Commissions (via recipients)
        try:
            res = await db.execute(text(f"SELECT COUNT(*) FROM commission_recipients WHERE company_id = '{company_id}'"))
            rec_count = res.scalar()
            print(f"\nCommission Recipients count: {rec_count}")
            
            if rec_count > 0:
                res = await db.execute(text(f"SELECT id FROM commission_recipients WHERE company_id = '{company_id}'"))
                rec_ids = [str(r[0]) for r in res]
                rec_ids_str = "', '".join(rec_ids)
                
                res = await db.execute(text(f"SELECT COUNT(*) FROM commissions WHERE recipient_id IN ('{rec_ids_str}')"))
                comm_count = res.scalar()
                print(f"Commissions count: {comm_count}")
                
                if comm_count > 0:
                    res = await db.execute(text(f"SELECT * FROM commissions WHERE recipient_id IN ('{rec_ids_str}') LIMIT 2"))
                    for row in res.mappings():
                        print(f" - Commission: {dict(row)}")
        except Exception as e:
            print(f"Error checking commissions: {e}")

asyncio.run(check_data())
