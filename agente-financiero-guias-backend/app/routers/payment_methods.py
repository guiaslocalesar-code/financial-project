from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional, List
from app.database import get_db
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

@router.post("", response_model=PaymentMethodResponse)
async def create_payment_method(pm_in: PaymentMethodCreate, db: AsyncSession = Depends(get_db)):
    payment_method = PaymentMethod(**pm_in.model_dump())
    db.add(payment_method)
    await db.commit()
    await db.refresh(payment_method)
    return payment_method

@router.get("", response_model=List[PaymentMethodResponse])
async def list_payment_methods(
    company_id: UUID,
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(PaymentMethod).where(PaymentMethod.company_id == company_id)
    if is_active is not None:
        query = query.where(PaymentMethod.is_active == is_active)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{pm_id}", response_model=PaymentMethodResponse)
async def get_payment_method(pm_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == pm_id))
    payment_method = result.scalar_one_or_none()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment_method

@router.put("/{pm_id}", response_model=PaymentMethodResponse)
async def update_payment_method(pm_id: str, pm_in: PaymentMethodUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == pm_id))
    payment_method = result.scalar_one_or_none()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    update_data = pm_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment_method, field, value)
    
    await db.commit()
    await db.refresh(payment_method)
    return payment_method

@router.delete("/{pm_id}")
async def delete_payment_method(pm_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == pm_id))
    payment_method = result.scalar_one_or_none()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    payment_method.is_active = False
    await db.commit()
    return {"message": "Payment method deactivated successfully"}
