import asyncio
from uuid import UUID
from app.database import AsyncSessionLocal
from app.services.dashboard_service import dashboard_service

company_id = UUID("aeb56588-5e15-4ce2-b24b-065ebf842c44")

async def test():
    async with AsyncSessionLocal() as db:
        try:
            res = await dashboard_service.get_commissions_summary(company_id=company_id, db=db)
            print("SUCCESS")
            print(res)
        except Exception as e:
            print("ERROR:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
