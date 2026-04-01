import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.models.client import Client
from app.utils.enums import TransactionType
from datetime import date

async def generate_report_file():
    async with SessionLocal() as db:
        # Query 1: Budgets grouped by client
        budget_query = select(
            Client.name,
            func.sum(IncomeBudget.budgeted_amount).label("planned")
        ).join(Client, IncomeBudget.client_id == Client.id)\
         .where(IncomeBudget.period_month == 3, IncomeBudget.period_year == 2026)\
         .group_by(Client.name)
        
        # Query 2: Real transactions grouped by client
        trans_query = select(
            Client.name,
            func.sum(Transaction.amount).label("collected")
        ).join(Client, Transaction.client_id == Client.id)\
         .where(
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date >= date(2026, 3, 1),
            Transaction.transaction_date <= date(2026, 3, 31)
        ).group_by(Client.name)

        budget_res = await db.execute(budget_query)
        trans_res = await db.execute(trans_query)

        budgets = {row.name: float(row.planned) for row in budget_res.all()}
        collected = {row.name: float(row.collected) for row in trans_res.all()}

        all_clients = sorted(set(budgets.keys()) | set(collected.keys()))

        report_content = """# Informe de Ingresos Cruzado - Marzo 2026

Este informe presenta la comparativa entre los ingresos proyectados (presupuestados) y los efectivamente cobrados durante el mes de marzo de 2026.

## 1. Origen de los Datos
La información se extrae de dos fuentes principales en el sistema:
*   **Tabla `income_budgets`**: Representa la "Planificación de Cobranza". Aquí figuran los montos que se esperan percibir de cada cliente por sus respectivos servicios. Es la fuente de la "proyección".
*   **Tabla `transactions`**: Representa el "Flujo de Caja Real". Aquí se registran los movimientos de dinero efectivamente realizados. Es donde verificamos qué se cobró realmente.

## 2. Resumen Ejecutivo
| Métrica | Valor Total |
|---|---|
| **Total Proyectado (Presupuesto)** | **${total_planned:,.2f}** |
| **Total Cobrado (Transacciones Reales)** | **${total_collected:,.2f}** |
| **Saldo Pendiente de Cobro** | **${total_pending:,.2f}** |

## 3. Desglose por Cliente
A continuación se detalla el estado de cuenta por cada cliente para este período:

| Cliente | Planificado | Cobrado | Pendiente |
|---|---|---|---|
"""
        total_p = 0
        total_c = 0
        total_pen = 0
        table_rows = ""
        
        for client in all_clients:
            p = budgets.get(client, 0.0)
            c = collected.get(client, 0.0)
            pen = max(0.0, p - c)
            total_p += p
            total_c += c
            total_pen += pen
            table_rows += f"| {client} | ${p:,.2f} | ${c:,.2f} | ${pen:,.2f} |\n"
        
        final_report = report_content.format(
            total_planned=total_p,
            total_collected=total_c,
            total_pending=total_pen
        ) + table_rows

        report_file = "reporte_ingresos_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Informe generado: {report_file}")

if __name__ == "__main__":
    asyncio.run(generate_report_file())
