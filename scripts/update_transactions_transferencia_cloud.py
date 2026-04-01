import asyncio
from sqlalchemy import update
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.utils.enums import PaymentMethod as PaymentMethodEnum

async def main():
    async with SessionLocal() as db:
        print("Updating Cloud SQL transactions...")
        # Update all transactions to pm_transferencia and transfer enum
        stmt = (
            update(Transaction)
            .values(
                payment_method=PaymentMethodEnum.TRANSFER,
                payment_method_id="pm_transferencia"
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Cloud SQL: Updated {result.rowcount} transactions.")

if __name__ == "__main__":
    asyncio.run(main())
