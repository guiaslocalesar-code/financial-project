import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.models.expense_type import ExpenseType
from app.utils.enums import TransactionType
from datetime import date

async def generate_expense_report():
    async with SessionLocal() as db:
        # Query 1: Budgets grouped by ExpenseType
        budget_query = select(
            ExpenseType.name,
            func.sum(ExpenseBudget.budgeted_amount).label("budgeted")
        ).join(ExpenseType, ExpenseBudget.expense_type_id == ExpenseType.id)\
         .where(ExpenseBudget.period_month == 3, ExpenseBudget.period_year == 2026)\
         .group_by(ExpenseType.name)
        
        # Query 2: Real transactions grouped by ExpenseType
        trans_query = select(
            ExpenseType.name,
            func.sum(Transaction.amount).label("paid")
        ).join(ExpenseType, Transaction.expense_type_id == ExpenseType.id)\
         .where(
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        ).group_by(ExpenseType.name)

        budget_res = await db.execute(budget_query)
        trans_res = await db.execute(trans_query)

        budgets = {row.name: float(row.budgeted) for row in budget_res.all()}
        paid = {row.name: float(row.paid) for row in trans_res.all()}

        all_types = sorted(set(budgets.keys()) | set(paid.keys()))

        report_content = """# Informe de Egresos Cruzado - Marzo 2026

Este informe presenta la comparativa entre los egresos proyectados (presupuestados) y los efectivamente pagados durante el mes de marzo de 2026.

## 1. Origen de los Datos
*   **Tabla `expense_budgets`**: Representa el "Presupuesto de Egresos". Es donde se planifican los costos fijos (sueldos, alquiler) y variables del mes.
*   **Tabla `transactions`**: Representa el "Flujo de Caja Real". Muestra los pagos que ya se han efectuado y restado del saldo.

## 2. Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Total Presupuestado** | **${total_budgeted:,.2f}** |
| **Total Pagado (Real)** | **${total_paid:,.2f}** |
| **Saldo Pendiente de Pago** | **${total_pending:,.2f}** |

## 3. Desglose por Tipo de Gasto
Comparativa de lo planificado vs. lo pagado por categoría:

| Categoría | Presupuestado | Pagado | Pendiente |
|---|---|---|---|
"""
        total_b = 0
        total_p = 0
        total_pen = 0
        table_rows = ""
        
        for etype in all_types:
            b = budgets.get(etype, 0.0)
            p = paid.get(etype, 0.0)
            pen = max(0.0, b - p)
            total_b += b
            total_p += p
            total_pen += pen
            table_rows += f"| {etype} | ${b:,.2f} | ${p:,.2f} | ${pen:,.2f} |\n"
        
        final_report = report_content.format(
            total_budgeted=total_b,
            total_paid=total_p,
            total_pending=total_pen
        ) + table_rows

        report_file = "reporte_egresos_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Informe generado: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_expense_report())
