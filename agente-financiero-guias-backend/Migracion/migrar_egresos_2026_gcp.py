import asyncio
import pandas as pd
from sqlalchemy import select
from app.database import SessionLocal
from app.models.company import Company
from app.models.expense_type import ExpenseType
from app.models.expense_category import ExpenseCategory
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.utils.enums import BudgetStatus, TransactionType, AppliesTo, ExpenseOrigin

async def main():
    async with SessionLocal() as db:
        # 1. Fetch Company
        res = await db.execute(select(Company).where(Company.name.ilike('%Guias%locales%')))
        company = res.scalars().first()
        if not company:
            res = await db.execute(select(Company).limit(1))
            company = res.scalar_one_or_none()
            if not company:
                print("Company not found.")
                return
        
        print(f"Using company: {company.name} ({company.id})")
        print("Migrating Egresos 2026 a GCP...")
        
        try:
            df = pd.read_csv('egresos 2026/FLUJO DE DINERO NEW - egresos 2026.csv')
            df.columns = df.columns.str.strip()
        except FileNotFoundError:
            print("CSV not found.")
            return

        # Clean Date and Amount
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, format='mixed', errors='coerce').dt.date
        df['ESTIMADO'] = df['ESTIMADO'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
        df = df.dropna(subset=['Fecha', 'ESTIMADO'])

        inserted_budgets = 0
        inserted_transactions = 0
        skipped = 0
        
        types_map = {}
        categories_map = {}

        count = 0
        for idx, row in df.iterrows():
            fecha = row['Fecha']
            monto = float(row['ESTIMADO'])
            tipo_name = str(row['Tipo']).strip().capitalize() if pd.notna(row['Tipo']) else "Otros"
            categoria_name = str(row['Egresos']).strip() if pd.notna(row['Egresos']) else "Varios"
            estado_raw = str(row['ESTADO']).strip().lower()
            
            es_pago = estado_raw == 'pago realizado'
            status = BudgetStatus.PAID if es_pago else BudgetStatus.PENDING
            
            origen_raw = str(row['Origen']).strip().lower() if pd.notna(row['Origen']) else ''
            
            # Upsert ExpenseType
            if tipo_name not in types_map:
                res_type = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company.id, ExpenseType.name == tipo_name))
                t = res_type.scalar_one_or_none()
                if not t:
                    t = ExpenseType(company_id=company.id, name=tipo_name, applies_to=AppliesTo.BOTH)
                    db.add(t)
                    await db.flush()
                types_map[tipo_name] = t.id
            
            type_id = types_map[tipo_name]
            
            # Upsert ExpenseCategory
            cat_key = f"{type_id}_{categoria_name}"
            if cat_key not in categories_map:
                res_cat = await db.execute(select(ExpenseCategory).where(ExpenseCategory.company_id == company.id, ExpenseCategory.expense_type_id == type_id, ExpenseCategory.name == categoria_name))
                c = res_cat.scalar_one_or_none()
                if not c:
                    c = ExpenseCategory(company_id=company.id, expense_type_id=type_id, name=categoria_name)
                    db.add(c)
                    await db.flush()
                categories_map[cat_key] = c.id
                
            cat_id = categories_map[cat_key]

            # Idempotence: check budget
            budget_check = await db.execute(select(ExpenseBudget).where(
                ExpenseBudget.company_id == company.id,
                ExpenseBudget.expense_category_id == cat_id,
                ExpenseBudget.planned_date == fecha,
                ExpenseBudget.budgeted_amount == monto
            ))
            budget = budget_check.scalar_one_or_none()
            
            if not budget:
                budget = ExpenseBudget(
                    company_id=company.id,
                    expense_type_id=type_id,
                    expense_category_id=cat_id,
                    description=categoria_name,
                    budgeted_amount=monto,
                    actual_amount=monto if es_pago else None,
                    planned_date=fecha,
                    period_month=fecha.month,
                    period_year=fecha.year,
                    is_recurring=False,
                    status=status
                )
                db.add(budget)
                await db.flush()
                inserted_budgets += 1
            else:
                if budget.status == BudgetStatus.PAID and es_pago:
                    skipped += 1
                    continue
                elif budget.status == BudgetStatus.PENDING and es_pago:
                    budget.status = BudgetStatus.PAID
                    budget.actual_amount = monto
                    await db.flush()
                else:
                    skipped += 1
                    continue

            # Transaction create
            if es_pago:
                is_budgeted = 'no ' not in origen_raw 
                origin = ExpenseOrigin.BUDGETED if is_budgeted else ExpenseOrigin.UNBUDGETED
                
                # Payment method logic (simple map for now as "other")
                pm_raw = str(row['Medio de Pago']).strip() if pd.notna(row['Medio de Pago']) else "other"
                
                transaction = Transaction(
                    company_id=company.id,
                    budget_id=budget.id,
                    expense_type_id=type_id,
                    expense_category_id=cat_id,
                    type=TransactionType.EXPENSE,
                    is_budgeted=is_budgeted,
                    expense_origin=origin,
                    amount=monto,
                    payment_method="other",
                    description=f"Pago {tipo_name} - {categoria_name} via {pm_raw}",
                    transaction_date=fecha
                )
                db.add(transaction)
                await db.flush()
                budget.transaction_id = transaction.id
                inserted_transactions += 1
            
            count += 1
            if count % 100 == 0:
                await db.commit()
                
        await db.commit()
        print(f"Egresos GCP stats: {inserted_budgets} budgets created, {inserted_transactions} transactions created. {skipped} duplicates skipped.")

if __name__ == "__main__":
    asyncio.run(main())
