import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.models.client import Client
from app.utils.enums import TransactionType

async def generate_client_report():
    async with SessionLocal() as db:
        # Query 1: Budgets grouped by client
        budget_query = select(
            Client.name,
            func.sum(IncomeBudget.budgeted_amount).label("planned")
        ).join(Client, IncomeBudget.client_id == Client.id)\
         .where(IncomeBudget.period_month == 3, IncomeBudget.period_year == 2026)\
         .group_by(Client.name)
        
        # Query 2: Real transactions grouped by client
        from datetime import date
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

        print("| Cliente | Planificado | Cobrado | Pendiente |")
        print("|---|---|---|---|")
        total_p = 0
        total_c = 0
        total_pen = 0
        for client in all_clients:
            p = budgets.get(client, 0.0)
            c = collected.get(client, 0.0)
            pen = max(0, p - c)
            total_p += p
            total_c += c
            total_pen += pen
            print(f"| {client} | ${p:,.2f} | ${c:,.2f} | ${pen:,.2f} |")
        
        print(f"\nTOTALES: Planificado: ${total_p:,.2f} | Cobrado: ${total_c:,.2f} | Pendiente: ${total_pen:,.2f}")

if __name__ == "__main__":
    asyncio.run(generate_client_report())
