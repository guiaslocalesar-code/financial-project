import asyncio
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.company import Company
from app.models.expense_type import ExpenseType
from app.models.expense_category import ExpenseCategory
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.utils.enums import BudgetStatus, TransactionType, ExpenseOrigin

async def main():
    async with SessionLocal() as db:
        result = await db.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()
        if not company:
            print("Company not found. Run migracion_catalogos first.")
            return

        print("Migrating Egresos (Expense Budgets and Transactions)...")
        try:
            df = pd.read_csv('Migracion/FLUJO DE DINERO NEW - Gastos FIJOS (14).csv')
        except FileNotFoundError:
            print("CSV Egresos not found.")
            return

        df['Fecha'] = pd.to_datetime(df['Fecha '], dayfirst=True, errors='coerce').dt.date
        df['ESTIMADO'] = df['ESTIMADO'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
        
        df_valid = df[df['ESTADO'] == 'Pago Realizado'].dropna(subset=['ESTIMADO'])
        
        inserted_budgets = 0
        inserted_transactions = 0
        skipped = 0
        
        # Mapping Types & Categories
        res_types = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company.id))
        types_map = {t.name: t.id for t in res_types.scalars()}
        
        res_cats = await db.execute(select(ExpenseCategory).where(ExpenseCategory.company_id == company.id))
        cats_map = {c.name: c.id for c in res_cats.scalars()} # Names are unique across types for this CSV data
        
        count = 0
        for _, row in df_valid.iterrows():
            if pd.isna(row['Fecha']):
                continue
                
            monto = float(row['ESTIMADO'])
            fecha = row['Fecha']
            origen = str(row['Origen'])
            tipo = str(row['Tipo']).strip()
            cat = str(row['Egresos']).strip()
            medio = str(row['Medio de Pago']).strip()
            
            payment_method = 'other'
            if medio in ['Mp1', 'Mp5']: payment_method = 'transfer'
            elif medio in ['Mp2', 'Mp3']: payment_method = 'card'
            
            exp_type_id = types_map.get(tipo)
            exp_cat_id = cats_map.get(cat)
            
            if not exp_type_id or not exp_cat_id:
                print(f"Warning: map missing '{tipo}' or '{cat}'. Skipping.")
                continue
            
            desc = str(row.get('Categoria', cat))
            
            # Idempotence Check - Transaction
            tx_check = await db.execute(select(Transaction).where(
                Transaction.company_id == company.id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.amount == monto,
                Transaction.transaction_date == fecha
            ))
            
            existing_tx = []
            for tx in tx_check.scalars():
                if tx.expense_category_id == exp_cat_id:
                    existing_tx.append(tx)
            
            if existing_tx:
                skipped += 1
                continue
                
            is_budgeted = 'No Presupuestado' not in origen
            budget_id = None
            
            # Idempotence Check - Budget
            if is_budgeted:
                budget_check = await db.execute(select(ExpenseBudget).where(
                    ExpenseBudget.company_id == company.id,
                    ExpenseBudget.expense_category_id == exp_cat_id,
                    ExpenseBudget.planned_date == fecha,
                    ExpenseBudget.budgeted_amount == monto
                ))
                budget = budget_check.scalar_one_or_none()
                if not budget:
                    budget = ExpenseBudget(
                        company_id=company.id,
                        expense_type_id=exp_type_id,
                        expense_category_id=exp_cat_id,
                        description=desc,
                        budgeted_amount=monto,
                        actual_amount=monto,
                        planned_date=fecha,
                        period_month=fecha.month,
                        period_year=fecha.year,
                        is_recurring=tipo in ['Sueldos', 'Oficina', 'Herramientas'],
                        status=BudgetStatus.PAID
                    )
                    db.add(budget)
                    await db.flush()
                    inserted_budgets += 1
                budget_id = budget.id
                
            # Create transaction
            transaction = Transaction(
                company_id=company.id,
                expense_type_id=exp_type_id,
                expense_category_id=exp_cat_id,
                budget_id=budget_id,
                type=TransactionType.EXPENSE,
                is_budgeted=is_budgeted,
                expense_origin=ExpenseOrigin.BUDGETED if is_budgeted else ExpenseOrigin.UNBUDGETED,
                amount=monto,
                payment_method=payment_method,
                description=desc,
                transaction_date=fecha
            )
            db.add(transaction)
            inserted_transactions += 1
            
            count += 1
            if count % 100 == 0:
                await db.commit() # batch commits
            
        await db.commit()
        print(f"Egresos stats: {inserted_budgets} budgets created, {inserted_transactions} transactions created. {skipped} duplicates skipped.")

if __name__ == "__main__":
    asyncio.run(main())
