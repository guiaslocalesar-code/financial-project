import asyncio
from datetime import date
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.models.expense_type import ExpenseType
from app.models.expense_category import ExpenseCategory
from app.utils.enums import TransactionType

async def check_migration():
    async with SessionLocal() as db:
        # 1. Categorías de egresos
        print("--- CATEGORIAS DE EGRESOS (MUESTRA) ---")
        q1 = await db.execute(select(ExpenseCategory.name).distinct().order_by(ExpenseCategory.name).limit(15))
        for row in q1:
            print(f"- {row[0]}")
        
        # 2. Ingresos Enero 2026
        print("\n--- INGRESOS ENERO 2026 ---")
        stmt2 = select(func.sum(Transaction.amount)).where(
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date >= date(2026, 1, 1),
            Transaction.transaction_date <= date(2026, 1, 31)
        )
        res2 = await db.execute(stmt2)
        total_jan = res2.scalar() or 0
        print(f"Total Ingresos Enero 2026: ${total_jan:,.2f}")

        # 3. Evolución gastos fijos último trimestre
        print("\n--- EVOLUCION GASTOS FIJOS (ULTIMO TRIMESTRE) ---")
        stmt3 = (
            select(
                func.extract('month', Transaction.transaction_date).label('month'),
                func.extract('year', Transaction.transaction_date).label('year'),
                func.sum(Transaction.amount).label('total')
            )
            .join(ExpenseType, Transaction.expense_type_id == ExpenseType.id)
            .where(
                ExpenseType.name.in_(['Sueldos', 'Oficina', 'Herramientas']),
                Transaction.transaction_date >= date(2025, 12, 1),
                Transaction.transaction_date <= date(2026, 2, 28)
            )
            .group_by('year', 'month')
            .order_by('year', 'month')
        )
        res3 = await db.execute(stmt3)
        for row in res3:
            print(f"Período {int(row[1])}-{int(row[0]):02d}: ${row[2]:,.2f}")

if __name__ == "__main__":
    asyncio.run(check_migration())
