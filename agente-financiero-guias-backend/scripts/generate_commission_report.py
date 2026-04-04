import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.commission import Commission
from app.models.commission_recipient import CommissionRecipient
from app.models.transaction import Transaction
from app.utils.enums import CommissionStatus
from datetime import date

async def generate_commission_report():
    async with SessionLocal() as db:
        # Consulta para obtener comisiones generadas por ingresos de Marzo 2026
        query = select(
            CommissionRecipient.name,
            func.sum(Commission.commission_amount).label("total_generated"),
            func.count(Commission.id).label("count"),
            func.sum(Commission.base_amount).label("total_base")
        ).join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)\
         .join(Transaction, Commission.income_transaction_id == Transaction.id)\
         .where(
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        ).group_by(CommissionRecipient.name)

        # Consulta para ver qué se pagó (Comisiones con pago asociado en Marzo 2026)
        paid_query = select(
            CommissionRecipient.name,
            func.sum(Commission.commission_amount).label("total_paid")
        ).join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id)\
         .where(Commission.status == CommissionStatus.PAID)\
         .join(Transaction, Commission.payment_transaction_id == Transaction.id)\
         .where(
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        ).group_by(CommissionRecipient.name)

        res = await db.execute(query)
        paid_res = await db.execute(paid_query)

        rows = res.all()
        paid_rows = paid_res.all()

        paid_dict = {row.name: float(row.total_paid) for row in paid_rows}

        report_content = """# Informe de Comisiones - Marzo 2026

Este informe detalla las comisiones generadas por los cobros realizados en marzo de 2026 y el estado de su liquidación.

## 🛠️ Estructura de Datos (Tablas Cruzadas)
Para este informe se cruzaron las siguientes tablas:
1.  **`commissions`**: Tabla principal que registra el monto de comisión y su estado (PENDING/PAID).
2.  **`commission_recipients`**: Contiene los nombres de los beneficiarios (vendedores/gestores).
3.  **`transactions`**: Se utilizó doblemente:
    *   Primero para filtrar las comisiones según la **fecha del ingreso** que las originó.
    *   Segundo para verificar si existe una **transacción de pago** realizada en el mes.

## 📊 Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Comisiones Generadas (Marzo)** | **${total_gen:,.2f}** |
| **Comisiones Pagadas en este mes** | **${total_paid:,.2f}** |
| **Saldo Pendiente de Liquidación** | **${total_pending:,.2f}** |

## 👥 Desglose por Beneficiario
Montos generados por las ventas/cobros de Marzo 2026:

| Beneficiario | Comisiones Generadas | Base Imponible (Cobros) | Cant. Operaciones | Pagado (en Marzo) |
|---|---|---|---|---|
"""
        total_gen = 0
        total_paid_all = 0
        table_rows = ""
        
        for row in rows:
            gen = float(row.total_generated)
            base = float(row.total_base)
            count = row.count
            paid = paid_dict.get(row.name, 0.0)
            
            total_gen += gen
            total_paid_all += paid
            
            table_rows += f"| {row.name} | ${gen:,.2f} | ${base:,.2f} | {count} | ${paid:,.2f} |\n"
        
        final_report = report_content.format(
            total_gen=total_gen,
            total_paid=total_paid_all,
            total_pending=total_gen - total_paid_all
        ) + table_rows

        report_file = "reporte_comisiones_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Informe de comisiones generado: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_commission_report())
