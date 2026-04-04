import asyncio
import uuid
from app.database import SessionLocal
from app.services.commission_service import commission_service
from app.schemas.commission import CommissionPay

async def test_pay():
    async with SessionLocal() as db:
        try:
            # Let's pick another pending commission to test empty payment method
            comm_id = uuid.UUID("3dcd888d-3031-4fe6-9c26-c26b53a9b4ad")
            payload = CommissionPay(
                payment_method="transfer",
                payment_date="2026-04-03",
                payment_method_id="", # Empty string, like frontend!
                actual_amount=38400
            )
            comm = await commission_service.pay_commission(comm_id, payload, db)
            print("SUCCESS! Commission paid with empty payment_method_id")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pay())
