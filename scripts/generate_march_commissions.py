import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.transaction import Transaction
from app.utils.enums import TransactionType
from app.services.commission_service import calculate_commissions_for_income
from datetime import date

async def generate_commissions():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 1. Obtener todos los ingresos de Marzo 2026
        query = select(Transaction.id).where(
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        )
        
        result = await db.execute(query)
        tx_ids = [row[0] for row in result.all()]
        
        print(f"Procesando {len(tx_ids)} transacciones de ingreso...")

        count_created = 0
        for tx_id in tx_ids:
            commissions = await calculate_commissions_for_income(db, tx_id)
            count_created += len(commissions)
        
        await db.commit()
        print(f"\n✅ Generación completada. Se crearon {count_created} registros de comisión.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(generate_commissions())
