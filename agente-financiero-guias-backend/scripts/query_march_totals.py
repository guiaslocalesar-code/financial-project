import asyncio
import csv
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.utils.enums import TransactionType
from datetime import date

async def query_totals():
    async with SessionLocal() as db:
        # Query all transactions for March 2026
        full_query = select(
            Transaction.id,
            Transaction.type,
            Transaction.amount,
            Transaction.transaction_date,
            Transaction.description,
            Transaction.payment_method
        ).where(
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        ).order_by(Transaction.transaction_date.asc())

        results = await db.execute(full_query)
        rows = results.all()

        csv_file = "marzo_2026_transacciones.csv"
        with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Tipo", "Monto", "Fecha", "Descripcion", "Metodo Pago"])
            for row in rows:
                writer.writerow([
                    str(row.id),
                    row.type.value if hasattr(row.type, 'value') else str(row.type),
                    f"{float(row.amount):.2f}",
                    row.transaction_date.isoformat(),
                    row.description or "",
                    row.payment_method.value if row.payment_method and hasattr(row.payment_method, 'value') else str(row.payment_method or "")
                ])

        print(f"✅ Se ha generado el archivo: {csv_file} con {len(rows)} registros.")

        # Recalculate totals for summary print
        income_total = sum(float(r.amount) for r in rows if r.type == TransactionType.INCOME)
        expense_total = sum(float(r.amount) for r in rows if r.type == TransactionType.EXPENSE)
        income_count = sum(1 for r in rows if r.type == TransactionType.INCOME)
        expense_count = sum(1 for r in rows if r.type == TransactionType.EXPENSE)

        print("-" * 50)
        print(f"📊 RESUMEN TRANSACCIONES MARZO 2026")
        print("-" * 50)
        print(f"✅ INGRESOS: ${income_total:,.2f} ({income_count} transacciones)")
        print(f"❌ EGRESOS:  ${expense_total:,.2f} ({expense_count} transacciones)")
        print("-" * 50)
        print(f"💰 BALANCE NETO: ${income_total - expense_total:,.2f}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(query_totals())
