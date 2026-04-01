import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, outerjoin
from app.config import settings
from app.models.transaction import Transaction
from app.models.commission import Commission
from app.utils.enums import TransactionType
from app.services.commission_service import calculate_commissions_for_income
from datetime import date

async def generate_commissions():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Buscar todas las transacciones de tipo INCOME que aún no tengan comisión
        query = (
            select(Transaction.id)
            .where(Transaction.type == TransactionType.INCOME)
            .outerjoin(Commission, Transaction.id == Commission.income_transaction_id)
            .where(Commission.id == None)  # Solo las que NO tienen comisión generada
            .order_by(Transaction.transaction_date.asc())
        )
        
        result = await db.execute(query)
        tx_ids = [row[0] for row in result.all()]
        
        total_tx = len(tx_ids)
        print(f"Buscando histórico... Se encontraron {total_tx} ingresos sin comisión.")

        count_created = 0
        batch_size = 50
        
        for i, tx_id in enumerate(tx_ids):
            commissions = await calculate_commissions_for_income(db, tx_id)
            count_created += len(commissions)
            
            # Commit en lotes
            if (i + 1) % batch_size == 0:
                await db.commit()
                print(f"Procesando: {i + 1}/{total_tx} transacciones... Comisiones generadas: {count_created}")
        
        # Commit final
        await db.commit()
        print(f"\n✅ Generación histórica completada. Se crearon {count_created} registros totales.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(generate_commissions())
