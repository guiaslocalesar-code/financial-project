import asyncio
import pandas as pd
from sqlalchemy import select
from app.database import get_db, SessionLocal
from app.models.company import Company
from app.models.service import Service
from app.models.expense_type import ExpenseType
from app.models.expense_category import ExpenseCategory
from app.utils.enums import FiscalCondition, AppliesTo

async def get_or_create_default_company(db) -> Company:
    result = await db.execute(select(Company).limit(1))
    company = result.scalar_one_or_none()
    if not company:
        company = Company(
            name="Agencia Marketing Migrada",
            cuit="30000000000",
            fiscal_condition=FiscalCondition.RI
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        print(f"Created default company: {company.name}")
    else:
        print(f"Using company: {company.name}")
    return company

async def main():
    async with SessionLocal() as db:
        company = await get_or_create_default_company(db)
        
        print("Migrating Catalogos (Services, Expense Types, Categories)...")
        # 1. Services (from Ingresos CSV)
        try:
            df_ingresos = pd.read_csv('Migracion/FLUJO DE DINERO NEW - FLUJO 2025 (11).csv')
            nombres_servicios = df_ingresos['Nombre'].dropna().unique()
            
            services_added = 0
            for nombre in nombres_servicios:
                nombre_clean = str(nombre).strip()
                result = await db.execute(select(Service).where(Service.company_id == company.id, Service.name == nombre_clean))
                if not result.scalar_one_or_none():
                    db.add(Service(company_id=company.id, name=nombre_clean))
                    services_added += 1
                    
            await db.commit()
            print(f"- Services added: {services_added}")
        except FileNotFoundError:
            print("CSV Ingresos not found. Skipping services.")
            
        # 2. Expense Types & Categories (from Egresos CSV)
        try:
            df_egresos = pd.read_csv('Migracion/FLUJO DE DINERO NEW - Gastos FIJOS (14).csv')
            
            tipos_egreso = df_egresos['Tipo'].dropna().unique()
            types_added = 0
            
            # Create/Get Types
            type_mapping = {}
            for tipo in tipos_egreso:
                tipo_limpio = str(tipo).strip()
                result = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company.id, ExpenseType.name == tipo_limpio))
                expense_type = result.scalar_one_or_none()
                if not expense_type:
                    expense_type = ExpenseType(company_id=company.id, name=tipo_limpio, applies_to=AppliesTo.BOTH)
                    db.add(expense_type)
                    types_added += 1
                type_mapping[tipo_limpio] = expense_type
                
            await db.commit()
            
            # Since we just committed, we might need to query them again to ensure we have IDs for new ones
            for tipo_limpio in type_mapping.keys():
                result = await db.execute(select(ExpenseType).where(ExpenseType.company_id == company.id, ExpenseType.name == tipo_limpio))
                type_mapping[tipo_limpio] = result.scalar_one()

            print(f"- Expense Types added: {types_added}")
            
            # Create/Get Categories
            categories_added = 0
            df_egresos_clean = df_egresos.dropna(subset=['Tipo', 'Egresos'])
            pairs = df_egresos_clean[['Tipo', 'Egresos']].drop_duplicates()
            
            for _, row in pairs.iterrows():
                tipo_limpio = str(row['Tipo']).strip()
                cat_limpia = str(row['Egresos']).strip()
                
                exp_type = type_mapping[tipo_limpio]
                
                result = await db.execute(select(ExpenseCategory).where(
                    ExpenseCategory.company_id == company.id, 
                    ExpenseCategory.expense_type_id == exp_type.id, 
                    ExpenseCategory.name == cat_limpia
                ))
                if not result.scalar_one_or_none():
                    db.add(ExpenseCategory(company_id=company.id, expense_type_id=exp_type.id, name=cat_limpia))
                    categories_added += 1
                    
            await db.commit()
            print(f"- Expense Categories added: {categories_added}")
        except FileNotFoundError:
            print("CSV Egresos not found. Skipping types and categories.")

if __name__ == "__main__":
    asyncio.run(main())
