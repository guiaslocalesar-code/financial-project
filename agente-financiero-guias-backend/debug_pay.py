import asyncio
import uuid
from app.database import SessionLocal
from app.services.commission_service import commission_service
from app.schemas.commission import CommissionPay

async def debug_pay():
    async with SessionLocal() as db:
        try:
            # Let's hit the exact logic for "c60d060e-645c-47d1-8bbb-2234422feff7"
            comm_id = uuid.UUID("c60d060e-645c-47d1-8bbb-2234422feff7")
            payload = CommissionPay(
                payment_method="cash",
                payment_date="2026-04-02",
                actual_amount=27600
            )
            comm = await commission_service.pay_commission(comm_id, payload, db)
            print("SUCCESS", comm)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_pay())
