import asyncio
import uuid
from app.database import SessionLocal
from app.services.commission_service import commission_service
from app.schemas.commission import CommissionPay

async def debug_pay():
    async with SessionLocal() as db:
        try:
            comm_id = uuid.UUID("64d37885-bbcf-4d2f-ab26-15a2a3ab55f0")
            payload = CommissionPay(
                payment_method="transfer",
                payment_date="2026-04-03",
                payment_method_id="pm_transferencia",
                actual_amount=23520
            )
            comm = await commission_service.pay_commission(comm_id, payload, db)
            print("SUCCESS", comm)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pay())
