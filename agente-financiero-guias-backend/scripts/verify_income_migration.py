
import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.income_budget import IncomeBudget
from app.models.service import Service
from app.models.client import Client
from app.utils.enums import TransactionType

async def verify():
    async with SessionLocal() as db:
        print("\n" + "="*50)
        print("VERIFICATION RESULTS (ORM)")
        print("="*50)
        
        # 1. Totales generales
        res_tx_count = await db.execute(select(func.count()).select_from(Transaction).where(Transaction.type == TransactionType.INCOME))
        res_ib_count = await db.execute(select(func.count()).select_from(IncomeBudget))
        
        tx_count = res_tx_count.scalar()
        ib_count = res_ib_count.scalar()
        
        print(f"Transactions (income): {tx_count}")
        print(f"Income Budgets: {ib_count}")
        
        # 2. Verificar que service_id son IDs reales (no montos)
        res_ids = await db.execute(select(Transaction.service_id).distinct().where(Transaction.type == TransactionType.INCOME).order_by(Transaction.service_id))
        ids = [row[0] for row in res_ids.fetchall()]
        print(f"Unique Service IDs in Transactions: {ids}")
        
        # 3. Verificar que amounts son montos reales (no IDs de servicio)
        res_stats = await db.execute(select(func.min(Transaction.amount), func.max(Transaction.amount), func.avg(Transaction.amount)).where(Transaction.type == TransactionType.INCOME))
        stats = res_stats.first()
        print(f"Stats - Min: {stats[0]}, Max: {stats[1]}, Avg: {stats[2]}")
        
        # 4. Verificar FKs correctas
        res_fks = await db.execute(select(func.count()).select_from(Transaction).join(Client).join(Service).where(Transaction.type == TransactionType.INCOME))
        print(f"FK Matches (Client+Service): {res_fks.scalar()}")
        
        print("="*50)

if __name__ == "__main__":
    asyncio.run(verify())
