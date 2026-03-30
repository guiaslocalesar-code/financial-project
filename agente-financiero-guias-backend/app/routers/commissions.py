from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional
from app.database import get_db
from app.models.commission import CommissionRecipient, CommissionRule, Commission
from app.schemas.commission import (
    CommissionRecipientCreate, CommissionRecipientResponse, CommissionRecipientUpdate,
    CommissionRuleCreate, CommissionRuleResponse, CommissionRuleUpdate,
    CommissionResponse, CommissionStatusUpdate
)
from app.models.transaction import Transaction
from app.models.client import Client
from app.models.service import Service
router = APIRouter(prefix="/commissions", tags=["Commissions"])

# Recipients
@router.post("/recipients", response_model=CommissionRecipientResponse)
async def create_recipient(rec_in: CommissionRecipientCreate, db: AsyncSession = Depends(get_db)):
    recipient = CommissionRecipient(**rec_in.model_dump())
    db.add(recipient)
    await db.commit()
    await db.refresh(recipient)
    return recipient

@router.patch("/recipients/{recipient_id}", response_model=CommissionRecipientResponse)
async def update_recipient(recipient_id: UUID, rec_in: CommissionRecipientUpdate, db: AsyncSession = Depends(get_db)):
    recipient = await db.get(CommissionRecipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    update_data = rec_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recipient, key, value)
    
    await db.commit()
    await db.refresh(recipient)
    return recipient

@router.delete("/recipients/{recipient_id}")
async def delete_recipient(recipient_id: UUID, db: AsyncSession = Depends(get_db)):
    recipient = await db.get(CommissionRecipient, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    await db.delete(recipient)
    await db.commit()
    return {"status": "success", "message": "Recipient deleted"}

from sqlalchemy.orm import selectinload, joinedload

@router.get("/recipients", response_model=list[CommissionRecipientResponse])
async def list_recipients(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CommissionRecipient)
        .options(selectinload(CommissionRecipient.rules))
        .where(CommissionRecipient.company_id == company_id)
    )
    return result.scalars().all()

# Rules
@router.get("/rules", response_model=list[CommissionRuleResponse])
async def list_rules(company_id: UUID, db: AsyncSession = Depends(get_db)):
    query = (
        select(CommissionRule)
        .options(
            joinedload(CommissionRule.recipient),
            joinedload(CommissionRule.client),
            joinedload(CommissionRule.service)
        )
        .join(CommissionRecipient, CommissionRule.recipient_id == CommissionRecipient.id)
        .where(CommissionRecipient.company_id == company_id)
    )
    result = await db.execute(query)
    rules = result.scalars().all()
    
    for rule in rules:
        if rule.recipient: setattr(rule, "recipient_name", rule.recipient.name)
        if rule.client: setattr(rule, "client_name", rule.client.name)
        if rule.service: setattr(rule, "service_name", rule.service.name)
            
    return rules

@router.post("/rules", response_model=CommissionRuleResponse)
async def create_rule(rule_in: CommissionRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = CommissionRule(**rule_in.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.patch("/rules/{rule_id}", response_model=CommissionRuleResponse)
async def update_rule(rule_id: UUID, rule_in: CommissionRuleUpdate, db: AsyncSession = Depends(get_db)):
    rule = await db.get(CommissionRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    update_data = rule_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    await db.commit()
    await db.refresh(rule)
    return rule

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    rule = await db.get(CommissionRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.delete(rule)
    await db.commit()
    return {"status": "success", "message": "Rule deleted"}

# Commissions
@router.get("", response_model=list[CommissionResponse])
async def list_commissions(
    company_id: Optional[UUID] = None,
    recipient_id: Optional[UUID] = None, 
    db: AsyncSession = Depends(get_db)
):
    query = select(Commission).options(
        joinedload(Commission.recipient),
        joinedload(Commission.transaction).joinedload(Transaction.client),
        joinedload(Commission.transaction).joinedload(Transaction.service)
    )
    
    if recipient_id:
        query = query.where(Commission.recipient_id == recipient_id)
    
    if company_id:
        query = query.join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id) \
                     .where(CommissionRecipient.company_id == company_id)
                     
    result = await db.execute(query)
    commissions = result.scalars().all()
    
    for comm in commissions:
        if comm.recipient:
            setattr(comm, "recipient_name", comm.recipient.name)
        if comm.transaction:
            setattr(comm, "transaction_description", comm.transaction.description)
            setattr(comm, "transaction_date", comm.transaction.transaction_date)
            if comm.transaction.client:
                setattr(comm, "client_name", comm.transaction.client.name)
                setattr(comm, "client_logo", comm.transaction.client.imagen)
            if comm.transaction.service:
                setattr(comm, "service_name", comm.transaction.service.name or comm.transaction.service.nombre)
                
    return commissions

@router.patch("/{commission_id}/status", response_model=CommissionResponse)
async def update_commission_status(
    commission_id: UUID, 
    status_in: CommissionStatusUpdate, 
    db: AsyncSession = Depends(get_db)
):
    commission = await db.get(Commission, commission_id)
    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")
    
    commission.status = status_in.status
    await db.commit()
    await db.refresh(commission)
    return commission
