
import asyncio
import pandas as pd
from decimal import Decimal
import re
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.company import Company
from app.models.client import Client
from app.models.service import Service
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.utils.enums import IncomeBudgetStatus, TransactionType, PaymentMethod

CSV_PATH = 'FLUJO DE DINERO NEW - FLUJO 2025 (12).csv'

async def main():
    async with SessionLocal() as db:
        # Get Company
        result = await db.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()
        if not company:
            print("❌ Company not found.")
            return
        
        COMPANY_ID = company.id
        print(f"Using Company ID: {COMPANY_ID}")

        print(f"Reading CSV: {CSV_PATH}")
        try:
            df = pd.read_csv(CSV_PATH)
        except FileNotFoundError:
            print(f"❌ CSV not found at {CSV_PATH}")
            return

        # NORMALIZACIÓN
        # Fecha: dd/mm/yyyy → date
        df['Fecha_clean'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce').dt.date

        # Pago Realizado: d/m/yyyy → date (Note: format might vary, dayfirst=True is safer if mixed)
        df['Pago_Realizado_clean'] = pd.to_datetime(df['Pago Realizado'], dayfirst=True, errors='coerce').dt.date

        # Estimado (MONTO REAL): limpiar "$", "," → decimal
        def clean_amount(val):
            if pd.isna(val): return 0.0
            s = str(val).replace('$', '').replace(',', '').strip()
            try:
                return float(s)
            except ValueError:
                return 0.0

        df['Estimado_clean'] = df['Estimado'].apply(clean_amount)

        # INGRESOS (SERVICE_ID): limpiar y convertir a string
        def clean_id(val):
            if pd.isna(val) or str(val).lower() == 'nan' or str(val).strip() == '':
                return ""
            s = str(val).strip()
            if s.endswith('.0'):
                s = s[:-2]
            return s

        df['INGRESOS_clean'] = df['INGRESOS'].apply(clean_id)
        df['CLIENTE_clean'] = df['CLIENTE'].apply(clean_id)

        # STATUS mapping
        status_map = {
            'Transaccion completada': IncomeBudgetStatus.COLLECTED,
            'Facturado': IncomeBudgetStatus.COLLECTED,
            'Pendiente': IncomeBudgetStatus.PENDING
        }
        df['status_clean'] = df['ESTADO'].map(status_map).fillna(IncomeBudgetStatus.PENDING)

        processed_count = 0
        skipped_client = 0
        skipped_service = 0
        skipped_duplicate = 0
        inserted_budgets = 0
        inserted_transactions = 0

        print("Starting migration process...")

        for index, row in df.iterrows():
            total_rows = len(df)
            if index % 100 == 0:
                print(f"Processing row {index}/{total_rows}...")

            client_input = str(row['CLIENTE_clean']).strip()
            service_id = str(row['INGRESOS_clean']).strip()
            amount = Decimal(str(row['Estimado_clean']))
            transaction_date = row['Fecha_clean']
            
            if pd.isna(transaction_date) or not service_id or not client_input:
                continue
                
            planned_date = row['Pago_Realizado_clean'] if pd.notna(row['Pago_Realizado_clean']) else transaction_date
            status = row['status_clean']
            nombre_ref = row['Nombre']

            # Lookup Client
            # 1. By ID
            client_res = await db.execute(select(Client).where(Client.id == client_input, Client.company_id == COMPANY_ID))
            client = client_res.scalar_one_or_none()
            
            if not client:
                # 2. By Name
                client_res = await db.execute(select(Client).where(Client.name == client_input, Client.company_id == COMPANY_ID))
                client = client_res.scalar_one_or_none()
            
            if not client:
                print(f"SKIP: client '{client_input}' no existe -> fila {nombre_ref} (index {index})")
                skipped_client += 1
                continue

            # Lookup Service
            service_res = await db.execute(select(Service).where(Service.id == service_id, Service.company_id == COMPANY_ID))
            service = service_res.scalar_one_or_none()

            if not service:
                print(f"SKIP: service_id '{service_id}' no existe -> fila {nombre_ref} (index {index})")
                skipped_service += 1
                continue

            # IDEMPOTENCIA
            existing_res = await db.execute(select(IncomeBudget).where(
                IncomeBudget.client_id == client.id,
                IncomeBudget.service_id == service.id,
                IncomeBudget.planned_date == transaction_date,
                IncomeBudget.budgeted_amount == amount,
                IncomeBudget.company_id == COMPANY_ID
            ))
            if existing_res.scalar_one_or_none():
                skipped_duplicate += 1
                continue

            # CREATE income_budget
            budget = IncomeBudget(
                company_id=COMPANY_ID,
                client_id=client.id,
                service_id=service.id,
                budgeted_amount=amount,
                actual_amount=amount if status == IncomeBudgetStatus.COLLECTED else None,
                planned_date=transaction_date,
                period_month=transaction_date.month,
                period_year=transaction_date.year,
                is_recurring=True,
                status=status
            )
            db.add(budget)
            await db.flush()
            inserted_budgets += 1

            # CREATE transaction solo si está cobrado
            if status == IncomeBudgetStatus.COLLECTED:
                transaction = Transaction(
                    company_id=COMPANY_ID,
                    type=TransactionType.INCOME,
                    client_id=client.id,
                    service_id=service.id,
                    amount=amount,
                    transaction_date=planned_date, # Use Pago Realizado as per logic
                    income_budget_id=budget.id,
                    is_budgeted=True,
                    description=f"Cobro {client.id} - {service.id}",
                    payment_method=PaymentMethod.OTHER,
                    currency='ARS'
                )
                db.add(transaction)
                await db.flush()
                budget.transaction_id = transaction.id
                inserted_transactions += 1

            processed_count += 1
            if processed_count % 100 == 0:
                await db.commit()

        await db.commit()
        
        print("\n" + "="*30)
        print("MIGRATION COMPLETE")
        print("="*30)
        print(f"Total rows processed: {len(df)}")
        print(f"Successfully migrated: {processed_count}")
        print(f"Budgets created: {inserted_budgets}")
        print(f"Transactions created: {inserted_transactions}")
        print(f"Skipped (Client not found): {skipped_client}")
        print(f"Skipped (Service not found): {skipped_service}")
        print(f"Skipped (Duplicate): {skipped_duplicate}")
        print("="*30)

if __name__ == "__main__":
    asyncio.run(main())
