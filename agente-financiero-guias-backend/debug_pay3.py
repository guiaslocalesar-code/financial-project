import asyncio
import uuid
from app.database import SessionLocal
from app.services.commission_service import commission_service
from app.schemas.commission import CommissionPay

async def test_pay():
    async with SessionLocal() as db:
        try:
            comm_id = uuid.UUID("db3bc117-63f8-48b3-8ad8-36257e0badaf")
            payload = CommissionPay(
                payment_method="transfer",
                payment_date="2026-04-03",
                payment_method_id="pm_transferencia",
                actual_amount=12000
            )
            comm = await commission_service.pay_commission(comm_id, payload, db)
            print("SUCCESS! Commission paid locally without error!")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pay())
