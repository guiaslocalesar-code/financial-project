from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Optional, List
from datetime import timedelta, date
from calendar import monthrange

from app.database import get_db
from app.models.debt import Debt
from app.models.debt_installment import DebtInstallment
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse, DebtInstallmentResponse, DebtInstallmentCreate

router = APIRouter(prefix="/debts", tags=["Debts"])

@router.post("", response_model=DebtResponse)
async def create_debt(debt_in: DebtCreate, db: AsyncSession = Depends(get_db)):
    data = debt_in.model_dump()
    
    # Calculate missing logical fields required by DB schema
    first_due_date = data.get("first_due_date") or date.today()
    data["first_due_date"] = first_due_date
    
    installments_count = debt_in.installments or 1
    installment_amount = data.get("installment_amount")
    if not installment_amount:
        installment_amount = round(debt_in.total_amount / installments_count, 2)
        data["installment_amount"] = installment_amount
        
    interest_total = data.get("interest_total")
    if interest_total is None:
        interest_total = debt_in.total_amount - debt_in.original_amount
        data["interest_total"] = interest_total
    
    debt = Debt(**data)
    db.add(debt)
    await db.flush()  # Generate debt.id
    
    current_date = first_due_date
    cap_amt = round(debt.original_amount / installments_count, 2)
    int_amt = round(debt.interest_total / installments_count, 2)
    
    for i in range(1, installments_count + 1):
        inst = DebtInstallment(
            debt_id=debt.id,
            installment_number=i,
            amount=installment_amount,
            capital_amount=cap_amt,
            interest_amount=int_amt,
            due_date=current_date,
            status="PENDING"
        )
        db.add(inst)
        
        # Advance 1 month
        days_in_month = monthrange(current_date.year, current_date.month)[1]
        current_date += timedelta(days=days_in_month)
        
    debt_id = debt.id
    await db.commit()
    
    # Reload the debt with installments to satisfy DebtResponse
    result = await db.execute(
        select(Debt)
        .options(joinedload(Debt.debt_installments))
        .where(Debt.id == debt_id)
    )
    return result.unique().scalar_one()

@router.get("", response_model=List[DebtResponse])
async def list_debts(
    company_id: UUID,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Debt).options(joinedload(Debt.debt_installments)).where(Debt.company_id == company_id)
    if status:
        query = query.where(Debt.status == status)
    
    result = await db.execute(query)
    return result.unique().scalars().all()

@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(debt_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Debt)
        .options(joinedload(Debt.debt_installments))
        .where(Debt.id == debt_id)
    )
    debt = result.unique().scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt

@router.post("/{debt_id}/installments", response_model=DebtInstallmentResponse)
async def create_installment(debt_id: UUID, inst_in: DebtInstallmentCreate, db: AsyncSession = Depends(get_db)):
    installment = DebtInstallment(**inst_in.model_dump())
    db.add(installment)
    await db.commit()
    await db.refresh(installment)
    return installment

@router.get("/{debt_id}/installments", response_model=List[DebtInstallmentResponse])
async def list_installments(debt_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DebtInstallment).where(DebtInstallment.debt_id == debt_id))
    return result.scalars().all()
