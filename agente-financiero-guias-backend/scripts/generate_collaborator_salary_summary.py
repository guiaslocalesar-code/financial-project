import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.utils.enums import TransactionType
from datetime import date
from collections import defaultdict

SUELDOS_TYPE_ID = "adc92130-eba1-4819-8700-e9b336317469"

async def generate_summary():
    async with SessionLocal() as db:
        # 1. Planned Salaries
        planned_query = select(
            ExpenseBudget.description,
            ExpenseBudget.budgeted_amount,
            ExpenseBudget.id
        ).where(
            ExpenseBudget.expense_type_id == SUELDOS_TYPE_ID,
            ExpenseBudget.period_month == 3,
            ExpenseBudget.period_year == 2026
        )
        
        # 2. Paid Salaries (Transactions)
        paid_query = select(
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

        planned_rows = planned_res.all()
        paid_rows = paid_res.all()

        # Build map for paid totals by budget_id
        paid_map = {}
        for p in paid_rows:
            if p.budget_id:
                paid_map[p.budget_id] = paid_map.get(p.budget_id, 0) + float(p.amount)

        # Aggregate by name (description)
        summary = defaultdict(lambda: {"planned": 0.0, "paid": 0.0})
        
        for pl in planned_rows:
            name = pl.description.strip()
            p_amt = float(pl.budgeted_amount)
            c_amt = paid_map.get(pl.id, 0.0)
            
            summary[name]["planned"] += p_amt
            summary[name]["paid"] += c_amt

        report_content = """# Resumen de Sueldos por Colaborador - Marzo 2026

Este informe consolida los pagos semanales y parciales para mostrar el total mensual proyectado y pagado a cada colaborador.

| Colaborador | Total Presupuestado | Total Pagado | Pendiente | % Cumplimiento |
|---|---|---|---|---|
"""
        total_p = 0
        total_c = 0
        table_rows = ""
        
        sorted_names = sorted(summary.keys())
        for name in sorted_names:
            p = summary[name]["planned"]
            c = summary[name]["paid"]
            pen = max(0.0, p - c)
            perc = (c / p * 100) if p > 0 else 0
            
            total_p += p
            total_c += c
            table_rows += f"| {name} | ${p:,.2f} | ${c:,.2f} | ${pen:,.2f} | {perc:.1f}% |\n"
        
        total_pen = total_p - total_c
        footer = f"\n| **TOTAL GENERAL** | **${total_p:,.2f}** | **${total_c:,.2f}** | **${total_pen:,.2f}** | **{(total_c/total_p*100):.1f}%** |\n"

        final_report = report_content + table_rows + footer

        report_file = "resumen_sueldos_colaboradores_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Resumen generado: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_summary())
