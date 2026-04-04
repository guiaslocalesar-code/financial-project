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
from app.schemas.commission import RecipientSummary, CommissionPay, BulkPayPayload

@router.get("", response_model=list[CommissionResponse])
async def list_commissions(
    company_id: Optional[UUID] = None,
    recipient_id: Optional[UUID] = None, 
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Commission).options(
        joinedload(Commission.recipient),
        joinedload(Commission.transaction).options(
            joinedload(Transaction.client),
            joinedload(Transaction.service),
            joinedload(Transaction.income_budget)
        )
    )
    
    if recipient_id:
        query = query.where(Commission.recipient_id == recipient_id)
    
    if company_id:
        query = query.join(CommissionRecipient, Commission.recipient_id == CommissionRecipient.id) \
                     .where(CommissionRecipient.company_id == company_id)
    
    # Filtering by Month/Year if provided
    if month and year:
        # We join with transaction to filter by transaction_date, 
        # or we could filter by created_at of the commission itself.
        # Financial context usually prefers the transaction_date.
        query = query.join(Transaction, Commission.transaction_id == Transaction.id) \
                     .where(
                         func.extract('month', Transaction.transaction_date) == month,
                         func.extract('year', Transaction.transaction_date) == year
                     )
                     
    result = await db.execute(query)
    commissions = result.scalars().all()
    # ... rest of the existing logic ...
    
    for comm in commissions:
        if comm.recipient:
            setattr(comm, "recipient_name", comm.recipient.name)
        
        if comm.transaction:
            setattr(comm, "transaction_description", comm.transaction.description)
            setattr(comm, "transaction_date", comm.transaction.transaction_date)
            setattr(comm, "was_invoiced", getattr(comm.transaction, 'requires_invoice', False))
            
            # Calculate base_amount and percentage if they are not in the model (DB)
            # but we can get them from the original income budget
            budget_amount = 0
            if comm.transaction.income_budget:
                budget_amount = float(comm.transaction.income_budget.budgeted_amount)
                setattr(comm, "base_amount", budget_amount)
                
                if budget_amount > 0:
                    percentage = (float(comm.amount) / budget_amount) * 100
                    setattr(comm, "commission_percentage", round(percentage, 2))

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

from app.schemas.commission import RecipientSummary, CommissionPay
from app.services.commission_service import commission_service
from app.utils.enums import CommissionStatus

@router.get("/recipient/{recipient_id}/summary", response_model=RecipientSummary)
async def get_recipient_summary(recipient_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CommissionRecipient).where(CommissionRecipient.id == recipient_id)
    )
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    comm_query = select(Commission).options(
        joinedload(Commission.transaction).options(
            joinedload(Transaction.client),
            joinedload(Transaction.service),
            joinedload(Transaction.income_budget)
        )
    ).where(Commission.recipient_id == recipient_id)
    
    comm_res = await db.execute(comm_query)
    commissions = comm_res.scalars().all()
    
    total_earned = sum(c.amount for c in commissions)
    total_pending = sum(c.amount for c in commissions if c.status == CommissionStatus.PENDING)
    total_paid = sum(c.amount for c in commissions if c.status == CommissionStatus.PAID)
    performance_pct = (total_paid / total_earned * 100) if total_earned > 0 else 0.0
    
    for comm in commissions:
        if comm.transaction:
            setattr(comm, "transaction_description", comm.transaction.description)
            setattr(comm, "transaction_date", comm.transaction.transaction_date)
            setattr(comm, "was_invoiced", getattr(comm.transaction, 'requires_invoice', False))
            
            # Calculate base_amount and percentage
            budget_amount = 0
            if comm.transaction.income_budget:
                budget_amount = float(comm.transaction.income_budget.budgeted_amount)
                setattr(comm, "base_amount", budget_amount)
                
                if budget_amount > 0:
                    percentage = (float(comm.amount) / budget_amount) * 100
                    setattr(comm, "commission_percentage", round(percentage, 2))
            if comm.transaction.client:
                setattr(comm, "client_name", comm.transaction.client.name)
                setattr(comm, "client_logo", comm.transaction.client.imagen)
            if comm.transaction.service:
                setattr(comm, "service_name", comm.transaction.service.name or comm.transaction.service.nombre)
                
    return {
        "id": recipient.id,
        "company_id": recipient.company_id,
        "name": recipient.name,
        "email": recipient.email,
        "cuit": getattr(recipient, 'cuit', None),
        "is_active": recipient.is_active,
        "type": getattr(recipient, 'type', None),
        "created_at": recipient.created_at,
        "updated_at": recipient.updated_at,
        "stats": {
            "total_earned": total_earned,
            "total_pending": total_pending,
            "performance_pct": performance_pct
        },
        "commissions": commissions,
        "rules": []
    }

@router.post("/generate")
async def generate_commissions(company_id: UUID, db: AsyncSession = Depends(get_db)):
    created = await commission_service.generate_commissions(company_id, db)
    return {"message": "Commissions generated successfully", "count": created}

@router.post("/{commission_id}/pay", response_model=CommissionResponse)
async def pay_commission(
    commission_id: UUID, 
    payload: CommissionPay, 
    db: AsyncSession = Depends(get_db)
):
    try:
        commission = await commission_service.pay_commission(commission_id, payload, db)
        
        # Rellenar relaciones para response model
        if commission.recipient:
            setattr(commission, "recipient_name", commission.recipient.name)
        if commission.transaction:
            setattr(commission, "transaction_description", commission.transaction.description)
            setattr(commission, "transaction_date", commission.transaction.transaction_date)
            if commission.transaction.client:
                setattr(commission, "client_name", commission.transaction.client.name)
                setattr(commission, "client_logo", commission.transaction.client.imagen)
            if commission.transaction.service:
                setattr(commission, "service_name", commission.transaction.service.name or commission.transaction.service.nombre)
                
        return commission
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-pay")
async def bulk_pay_commissions(
    payload: BulkPayPayload,
    db: AsyncSession = Depends(get_db)
):
    try:
        results = await commission_service.bulk_pay_commissions(payload, db)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
