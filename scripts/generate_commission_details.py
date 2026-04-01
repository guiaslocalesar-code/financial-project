import asyncio
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.commission import Commission
from app.models.commission_rule import CommissionRule
from app.models.client import Client
from app.models.service import Service
from app.models.transaction import Transaction
from datetime import date

async def generate_commission_details():
    async with SessionLocal() as db:
        query = (
            select(
                Transaction.transaction_date,
                Client.name.label("client_name"),
                Service.name.label("service_name"),
                Commission.base_amount,
                CommissionRule.percentage,
                Commission.commission_amount
            )
            .select_from(Commission)
            .join(Client, Commission.client_id == Client.id)
            .join(Service, Commission.service_id == Service.id)
            .join(CommissionRule, Commission.commission_rule_id == CommissionRule.id)
            .join(Transaction, Commission.income_transaction_id == Transaction.id)
            .where(
                Transaction.transaction_date >= date(2026, 3, 1),
                Transaction.transaction_date <= date(2026, 3, 31)
            )
            .order_by(Transaction.transaction_date)
        )

        result = await db.execute(query)
        rows = result.all()

        report_content = """# Desglose Detallado de Comisiones - Marzo 2026

A continuación se presenta el detalle de cada una de las operaciones que generaron comisiones en marzo de 2026.

| Fecha | Cliente | Servicio | Base Imponible (Ingreso) | % Comisión | Comisión a Pagar ($) |
|---|---|---|---|---|---|
"""
        table_rows = ""
        total_base = 0
        total_comm = 0
        
        for row in rows:
            t_date = row.transaction_date.strftime("%Y-%m-%d")
            c_name = row.client_name
            s_name = row.service_name
            base = float(row.base_amount)
            pct = float(row.percentage)
            comm = float(row.commission_amount)
            
            total_base += base
            total_comm += comm
            
            table_rows += f"| {t_date} | {c_name} | {s_name} | ${base:,.2f} | {pct:.2f}% | ${comm:,.2f} |\n"
        
        footer = f"\n| **TOTALES** | | | **${total_base:,.2f}** | | **${total_comm:,.2f}** |\n"

        final_report = report_content + table_rows + footer

        report_file = "detalle_comisiones_marzo_2026.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"✅ Desglose detallado generado: {report_file} con {len(rows)} operaciones.")

if __name__ == "__main__":
    asyncio.run(generate_commission_details())
