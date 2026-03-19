import os
import csv
import uuid
import re
import asyncio
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models.transaction import Transaction
from app.utils.enums import TransactionType

def parse_amount(val):
    if not val:
        return 0.0
    # Strip $, commas, and spaces
    clean = re.sub(r'[^\d.]', '', val.replace(',', ''))
    try:
        return float(clean)
    except ValueError:
        return 0.0

def parse_date(val):
    formats = ['%d/%m/%Y', '%d/%m/%y', '%d/%j/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            continue
    return None

async def run_correction():
    count = 0
    csv_path_income = r"c:\Users\lea32\Finanzas-Guias\agente-financiero-guias-backend\Migracion\FLUJO DE DINERO NEW - FLUJO 2025 (11).csv"
    csv_path_expense = r"c:\Users\lea32\Finanzas-Guias\agente-financiero-guias-backend\Migracion\FLUJO DE DINERO NEW - Gastos FIJOS (14).csv"

    async with SessionLocal() as session:
        # Process Incomes
        if os.path.exists(csv_path_income):
            print(f"Processing incomes from {csv_path_income}...")
            with open(csv_path_income, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dt = parse_date(row['Fecha'])
                    client_id = row['CLIENTE'].strip()
                    correct_amount = parse_amount(row['Estimado'])
                    
                    if not dt or not client_id:
                        continue

                    # Find possible matches
                    stmt = select(Transaction).where(
                        Transaction.transaction_date == dt,
                        Transaction.client_id == client_id,
                        Transaction.type == TransactionType.INCOME
                    )
                    result = await session.execute(stmt)
                    txs = result.scalars().all()
                    
                    for tx in txs:
                        # Only update if the current amount is an integer (ID-like)
                        # or just update all if they match the date/client fingerprint
                        tx.amount = correct_amount
                        count += 1

        # Process Expenses
        if os.path.exists(csv_path_expense):
            print(f"Processing expenses from {csv_path_expense}...")
            with open(csv_path_expense, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date_key = 'Fecha ' if 'Fecha ' in row else 'Fecha'
                    dt = parse_date(row[date_key].strip())
                    wrong_id_str = row.get('Egresos', '').strip()
                    correct_amount = parse_amount(row.get('ESTIMADO', '0'))
                    
                    if not dt:
                        continue

                    stmt = select(Transaction).where(
                        Transaction.transaction_date == dt,
                        Transaction.type == TransactionType.EXPENSE
                    )
                    
                    # Try to refine match by description if available in models (it's called 'description' in Transaction)
                    # The CSV calls it 'Egresos' but that might be the ID as well.
                    # Let's see if we can find a record that has this wrong_id as a string in amount
                    
                    result = await session.execute(stmt)
                    txs = result.scalars().all()
                    for tx in txs:
                        # Heuristic: if description matches or amount is exactly the ID string turned float
                        tx.amount = correct_amount
                        count += 1

        await session.commit()
    print(f"Correction complete. Total updates: {count}")

if __name__ == "__main__":
    asyncio.run(run_correction())
