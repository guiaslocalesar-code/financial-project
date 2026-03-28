from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Optional
from app.database import get_db
from app.models.debt import Debt, DebtInstallment
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse, DebtInstallmentResponse, DebtInstallmentCreate

router = APIRouter(prefix="/debts", tags=["Debts"])

@router.post("", response_model=DebtResponse)
async def create_debt(debt_in: DebtCreate, db: AsyncSession = Depends(get_db)):
    debt = Debt(**debt_in.model_dump())
    db.add(debt)
    await db.commit()
    await db.refresh(debt)
    return debt

@router.get("", response_model=list[DebtResponse])
async def list_debts(
    company_id: UUID,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Debt).options(joinedload(Debt.debt_installments)).where(Debt.company_id == company_id)
    if status:
        query = query.where(Debt.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(debt_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Debt).options(joinedload(Debt.debt_installments)).where(Debt.id == debt_id))
    debt = result.scalar_one_or_none()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt

@router.post("/{debt_id}/installments", response_model=DebtInstallmentResponse)
async def create_installment(debt_id: str, inst_in: DebtInstallmentCreate, db: AsyncSession = Depends(get_db)):
    installment = DebtInstallment(**inst_in.model_dump())
    db.add(installment)
    await db.commit()
    await db.refresh(installment)
    return installment

@router.get("/{debt_id}/installments", response_model=list[DebtInstallmentResponse])
async def list_installments(debt_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DebtInstallment).where(DebtInstallment.debt_id == debt_id))
    return result.scalars().all()
