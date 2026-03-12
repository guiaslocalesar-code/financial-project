import asyncio
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.company import Company
from app.models.client import Client
from app.models.service import Service
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.utils.enums import FiscalCondition, IncomeBudgetStatus, TransactionType

async def main():
    async with SessionLocal() as db:
        result = await db.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()
        if not company:
            print("Company not found. Run migracion_catalogos first.")
            return

        print("Migrating Ingresos (Income Budgets and Transactions)...")
        try:
            df = pd.read_csv('Migracion/FLUJO DE DINERO NEW - FLUJO 2025 (11).csv')
        except FileNotFoundError:
            print("CSV Ingresos not found.")
            return

        # Normalize date and incomes
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce').dt.date
        df['INGRESOS'] = df['INGRESOS'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
        
        # Filter expected rows
        df_valid = df[df['ESTADO'] == 'Transaccion completada'].dropna(subset=['Fecha', 'INGRESOS'])
        
        inserted_budgets = 0
        inserted_transactions = 0
        skipped = 0
        
        # Mapping Services
        res_services = await db.execute(select(Service).where(Service.company_id == company.id))
        services_map = {s.name: s.id for s in res_services.scalars()}
        default_service_id = list(services_map.values())[0] if services_map else None

        # Caching Clients
        res_clients = await db.execute(select(Client).where(Client.company_id == company.id))
        clients_map = {c.name: c.id for c in res_clients.scalars()}
        
        count = 0
        for _, row in df_valid.iterrows():
            cliente_nombre = str(row['Nombre']).strip() if pd.notna(row['Nombre']) else str(row['CLIENTE']).strip()
            if cliente_nombre == 'nan':
                 cliente_nombre = "Cliente Indefinido"

            fecha = row['Fecha']
            monto = float(row['INGRESOS'])
            
            # Client lookup/create
            if cliente_nombre not in clients_map:
                new_client = Client(
                    company_id=company.id,
                    name=cliente_nombre,
                    cuit_cuil_dni=f"20000000000",
                    fiscal_condition=FiscalCondition.CONSUMIDOR_FINAL
                )
                db.add(new_client)
                await db.flush()
                clients_map[cliente_nombre] = new_client.id
            
            client_id = clients_map[cliente_nombre]
            service_id = services_map.get(cliente_nombre, default_service_id)
            
            # Idempotence Check - Transaction
            tx_check = await db.execute(select(Transaction).where(
                Transaction.company_id == company.id,
                Transaction.type == TransactionType.INCOME,
                Transaction.client_id == client_id,
                Transaction.amount == monto,
                Transaction.transaction_date == fecha
            ))
            
            if tx_check.scalar_one_or_none():
                skipped += 1
                continue
                
            # Idempotence Check - Income Budget
            budget_check = await db.execute(select(IncomeBudget).where(
                IncomeBudget.company_id == company.id,
                IncomeBudget.client_id == client_id,
                IncomeBudget.planned_date == fecha,
                IncomeBudget.budgeted_amount == monto
            ))
            budget = budget_check.scalar_one_or_none()
            
            if not budget:
                budget = IncomeBudget(
                    company_id=company.id,
                    client_id=client_id,
                    service_id=service_id,
                    budgeted_amount=monto,
                    actual_amount=monto,
                    planned_date=fecha,
                    period_month=fecha.month,
                    period_year=fecha.year,
                    is_recurring=True,
                    status=IncomeBudgetStatus.COLLECTED
                )
                db.add(budget)
                await db.flush()
                inserted_budgets += 1
                
            # Transaction creation
            transaction = Transaction(
                company_id=company.id,
                client_id=client_id,
                service_id=service_id,
                income_budget_id=budget.id,
                type=TransactionType.INCOME,
                is_budgeted=True,
                amount=monto,
                payment_method="other",
                description=f"Cobro {cliente_nombre}",
                transaction_date=fecha
            )
            db.add(transaction)
            inserted_transactions += 1
            
            count += 1
            if count % 100 == 0:
                await db.commit() # batch commits

        await db.commit()
        print(f"Ingresos stats: {inserted_budgets} budgets created, {inserted_transactions} transactions created. {skipped} duplicates skipped.")

if __name__ == "__main__":
    asyncio.run(main())
