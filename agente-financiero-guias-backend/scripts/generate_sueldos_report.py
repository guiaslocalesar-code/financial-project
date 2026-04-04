import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.utils.enums import TransactionType, BudgetStatus
from datetime import date

SUELDOS_TYPE_ID = "adc92130-eba1-4819-8700-e9b336317469"

async def generate_sueldos_report():
    async with SessionLocal() as db:
        # 1. Planned Salaries
        planned_query = select(
            ExpenseBudget.description,
            ExpenseBudget.budgeted_amount,
            ExpenseBudget.status,
            ExpenseBudget.id
        ).where(
            ExpenseBudget.expense_type_id == SUELDOS_TYPE_ID,
            ExpenseBudget.period_month == 3,
            ExpenseBudget.period_year == 2026
        ).order_by(ExpenseBudget.budgeted_amount.desc())
        
        # 2. Paid Salaries (Transactions)
        paid_query = select(
            Transaction.description,
            Transaction.amount,
            Transaction.budget_id
        ).where(
            Transaction.expense_type_id == SUELDOS_TYPE_ID,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        )

        planned_res = await db.execute(planned_query)
        paid_res = await db.execute(paid_query)

        planned = planned_res.all()
        paid = paid_res.all()

        # Build maps for paid totals
        paid_map = {}
        for p in paid:
            if p.budget_id:
                paid_map[p.budget_id] = paid_map.get(p.budget_id, 0) + float(p.amount)

        report_content = """# Detalle de Sueldos - Marzo 2026

Este informe detalla la asignación de dinero para salarios en el mes de marzo de 2026, comparando lo planificado contra los pagos realizados.

## ⚙️ Lógica de Cruce de Datos
Para generar este informe, se cruzaron las siguientes tablas de la base de datos:
1.  **`expense_types`**: Se filtró por la categoría `adc92130-eba1-4819-8631-746936317469` (Sueldos).
2.  **`expense_budgets`**: Es el origen de la planificación nominal. Cada fila representa un sueldo devengado para una persona o ítem específico.
3.  **`transactions`**: Muestra los pagos reales. Cada transacción de egreso vinculada a la categoría de Sueldos se restó del monto presupuestado correspondiente para determinar el saldo.

## 📊 Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Presupuesto Total Sueldos** | **${total_p:,.2f}** |
| **Total Pagado a la Fecha** | **${total_c:,.2f}** |
| **Saldos Pendientes** | **${total_pen:,.2f}** |

## 👥 Desglose Nominal
Estado de pago para cada ítem de sueldo presupuestado:

| Descripción | Presupuestado | Pagado | Pendiente | Estado |
|---|---|---|---|---|
"""
        total_p = 0
        total_c = 0
        total_pen = 0
        table_rows = ""
        
        for pl in planned:
            p_amt = float(pl.budgeted_amount)
            c_amt = paid_map.get(pl.id, 0.0)
            pen = max(0.0, p_amt - c_amt)
            total_p += p_amt
            total_c += c_amt
            total_pen += pen
            
            # Use status string from enum
            status_text = pl.status.value if hasattr(pl.status, 'value') else str(pl.status)
            table_rows += f"| {pl.description} | ${p_amt:,.2f} | ${c_amt:,.2f} | ${pen:,.2f} | {status_text} |\n"
        
        final_report = report_content.format(
            total_p=total_p,
            total_c=total_c,
            total_pen=total_pen
        ) + table_rows

        report_file = "detalle_sueldos_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Informe generado: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_sueldos_report())
