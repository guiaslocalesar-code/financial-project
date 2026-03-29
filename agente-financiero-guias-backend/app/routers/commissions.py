from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional
from app.database import get_db
from app.models.commission import CommissionRecipient, CommissionRule, Commission
from app.schemas.commission import (
    CommissionRecipientCreate, CommissionRecipientResponse,
    CommissionRuleCreate, CommissionRuleResponse,
    CommissionResponse
)

router = APIRouter(prefix="/commissions", tags=["Commissions"])

# Recipients
@router.post("/recipients", response_model=CommissionRecipientResponse)
async def create_recipient(rec_in: CommissionRecipientCreate, db: AsyncSession = Depends(get_db)):
    recipient = CommissionRecipient(**rec_in.model_dump())
    db.add(recipient)
    await db.commit()
    await db.refresh(recipient)
    return recipient

@router.get("/recipients", response_model=list[CommissionRecipientResponse])
async def list_recipients(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommissionRecipient).where(CommissionRecipient.company_id == company_id))
    return result.scalars().all()

# Rules
@router.get("/rules", response_model=list[CommissionRuleResponse])
async def list_rules(company_id: UUID, db: AsyncSession = Depends(get_db)):
    query = (
        select(CommissionRule)
        .join(CommissionRecipient, CommissionRule.recipient_id == CommissionRecipient.id)
        .where(CommissionRecipient.company_id == company_id)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/rules", response_model=CommissionRuleResponse)
async def create_rule(rule_in: CommissionRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = CommissionRule(**rule_in.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

# Commissions
@router.get("", response_model=list[CommissionResponse])
async def list_commissions(
    company_id: Optional[UUID] = None,
    recipient_id: Optional[UUID] = None, 
    db: AsyncSession = Depends(get_db)
):
    query = select(Commission)
    if recipient_id:
        query = query.where(Commission.recipient_id == str(recipient_id))
    
    if company_id:
        query = query.join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id) \
                     .where(CommissionRecipient.company_id == company_id)
                     
    result = await db.execute(query)
    return result.scalars().all()
