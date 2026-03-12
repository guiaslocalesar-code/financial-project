import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models.payment_method import PaymentMethod
from app.models.company import Company

async def seed_payment_methods():
    async with SessionLocal() as db:
        # Get all companies
        result = await db.execute(select(Company))
        companies = result.scalars().all()

        for company in companies:
            methods = [
                ('pm_efectivo', 'Efectivo', 'cash', False),
                ('pm_transferencia', 'Transferencia', 'transfer', False),
                ('pm_mp', 'Mercado Pago', 'transfer', False),
                ('pm_debito', 'Débito', 'debit_card', False),
                ('pm_credito', 'Crédito 1 cuota', 'credit_card', True),
                ('pm_financiacion', 'Financiación', 'financing', True)
            ]

            for pm_id, name, ptype, is_credit in methods:
                # Check if exists
                res_exists = await db.execute(select(PaymentMethod).where(PaymentMethod.id == pm_id, PaymentMethod.company_id == company.id))
                if not res_exists.scalar_one_or_none():
                    db.add(PaymentMethod(
                        id=pm_id,
                        company_id=company.id,
                        name=name,
                        type=ptype,
                        is_credit=is_credit
                    ))
        
        await db.commit()
    print("Payment methods seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_payment_methods())
