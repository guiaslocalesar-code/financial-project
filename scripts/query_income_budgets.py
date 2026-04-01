import asyncio
import csv
from sqlalchemy import select
from app.database import SessionLocal
from app.models.income_budget import IncomeBudget
from app.models.client import Client
from app.models.service import Service

async def query_income_budgets():
    async with SessionLocal() as db:
        # Consulta para obtener los ingresos planificados con nombres de cliente y servicio
        query = select(
            IncomeBudget.id,
            Client.name.label("client_name"),
            Service.name.label("service_name"),
            IncomeBudget.budgeted_amount,
            IncomeBudget.actual_amount,
            IncomeBudget.status,
            IncomeBudget.planned_date,
            IncomeBudget.period_month,
            IncomeBudget.period_year
        ).join(Client, IncomeBudget.client_id == Client.id)\
         .join(Service, IncomeBudget.service_id == Service.id)\
         .where(
            IncomeBudget.period_month == 3,
            IncomeBudget.period_year == 2026
        ).order_by(IncomeBudget.planned_date.asc())

        results = await db.execute(query)
        rows = results.all()

        csv_file = "ingresos_planificados_marzo_2026.csv"
        with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Cliente", "Servicio", "Monto Presupuestado", "Monto Real", "Estado", "Fecha Planificada", "Mes", "Año"])
            for row in rows:
                writer.writerow([
                    str(row.id),
                    row.client_name,
                    row.service_name,
                    f"{float(row.budgeted_amount):.2f}",
                    f"{float(row.actual_amount):.2f}" if row.actual_amount is not None else "0.00",
                    row.status.value if hasattr(row.status, 'value') else str(row.status),
                    row.planned_date.isoformat(),
                    row.period_month,
                    row.period_year
                ])

        print(f"✅ Se ha generado el archivo: {csv_file} con {len(rows)} registros.")

if __name__ == "__main__":
    asyncio.run(query_income_budgets())
