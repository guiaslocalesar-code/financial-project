import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import UUID
from datetime import date
from typing import List, Optional

from app.database import get_db
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule
from app.models.commission import Commission
from app.models.transaction import Transaction
from app.utils.enums import CommissionStatus, TransactionType, RecipientType
from app.schemas.commission import (
    CommissionRecipientCreate, CommissionRecipientUpdate, CommissionRecipientResponse,
    CommissionRuleCreate, CommissionRuleUpdate, CommissionRuleResponse,
    CommissionResponse, RecipientSummary, CommissionsDashboard, TopRecipient
)
from app.services.commission_service import calculate_commissions_for_income

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Commissions"])


# ── Commission Recipients CRUD ─────────────────────────────────────────────────

@router.post("/commission-recipients", response_model=CommissionRecipientResponse)
async def create_recipient(body: CommissionRecipientCreate, db: AsyncSession = Depends(get_db)):
    recipient = CommissionRecipient(**body.model_dump())
    db.add(recipient)
    await db.commit()
    await db.refresh(recipient)
    return recipient


@router.get("/commission-recipients", response_model=List[CommissionRecipientResponse])
async def list_recipients(
    company_id: UUID,
    only_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    q = select(CommissionRecipient).where(CommissionRecipient.company_id == company_id)
    if only_active:
        q = q.where(CommissionRecipient.is_active == True)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/commission-recipients/{recipient_id}", response_model=CommissionRecipientResponse)
async def update_recipient(
    recipient_id: UUID,
    body: CommissionRecipientUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == recipient_id))
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(recipient, field, value)
    await db.commit()
    await db.refresh(recipient)
    return recipient


@router.delete("/commission-recipients/{recipient_id}", status_code=204)
async def delete_recipient(recipient_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == recipient_id))
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient not found")
    recipient.is_active = False
    await db.commit()


# ── Commission Rules CRUD ──────────────────────────────────────────────────────

@router.post("/commission-rules", response_model=CommissionRuleResponse)
async def create_rule(body: CommissionRuleCreate, db: AsyncSession = Depends(get_db)):
    # Verify recipient exists
    r = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == body.recipient_id))
    if not r.scalar_one_or_none():
        raise HTTPException(400, "Recipient not found")
    try:
        rule = CommissionRule(**body.model_dump())
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule
    except Exception as e:
        await db.rollback()
        if "uq_commission_rule" in str(e):
            raise HTTPException(400, "Ya existe una regla para este recipient/cliente/servicio")
        raise HTTPException(500, str(e))


@router.get("/commission-rules", response_model=List[CommissionRuleResponse])
async def list_rules(
    company_id: UUID,
    only_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    q = select(CommissionRule).where(CommissionRule.company_id == company_id)
    if only_active:
        q = q.where(CommissionRule.is_active == True)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/commission-rules/{rule_id}", response_model=CommissionRuleResponse)
async def update_rule(
    rule_id: UUID,
    body: CommissionRuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CommissionRule).where(CommissionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Rule not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/commission-rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommissionRule).where(CommissionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Rule not found")
    rule.is_active = False
    await db.commit()


# ── Commissions Management ─────────────────────────────────────────────────────

@router.get("/commissions/pending", response_model=List[CommissionResponse])
async def get_pending_commissions(company_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Commission)
        .where(
            Commission.company_id == company_id,
            Commission.status == CommissionStatus.PENDING
        )
        .order_by(Commission.created_at.desc())
    )
    commissions = result.scalars().all()

    # Enrich with recipient name
    output = []
    for c in commissions:
        r = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == c.recipient_id))
        rec = r.scalar_one_or_none()
        item = CommissionResponse.model_validate(c)
        item.recipient_name = rec.name if rec else None
        output.append(item)
    return output


@router.post("/commissions/{commission_id}/pay")
async def pay_commission(commission_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Commission).where(Commission.id == commission_id))
    commission = result.scalar_one_or_none()
    if not commission:
        raise HTTPException(404, "Commission not found")
    if commission.status != CommissionStatus.PENDING:
        raise HTTPException(400, f"La comisión ya está en estado '{commission.status}'")

    # Obtener nombre del recipient para la descripción
    r = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == commission.recipient_id))
    recipient = r.scalar_one_or_none()
    recipient_name = recipient.name if recipient else "Desconocido"

    # Crear transaction de egreso
    expense_tx = Transaction(
        company_id=commission.company_id,
        type=TransactionType.EXPENSE,
        is_budgeted=False,
        amount=float(commission.commission_amount),
        description=f"Pago comisión a {recipient_name} — {commission.service_id}",
        transaction_date=date.today(),
    )
    db.add(expense_tx)
    await db.flush()

    commission.status = CommissionStatus.PAID
    commission.payment_transaction_id = expense_tx.id

    await db.commit()
    return {"transaction_id": str(expense_tx.id), "message": "Comisión pagada"}


@router.post("/commissions/generate")
async def generate_missing_commissions(company_id: UUID, db: AsyncSession = Depends(get_db)):
    """Recalcula comisiones para ingresos que aún no las tienen."""
    # IDs de ingresos que ya tienen comisión
    existing = await db.execute(
        select(Commission.income_transaction_id).where(Commission.company_id == company_id)
    )
    existing_ids = {row[0] for row in existing.all()}

    # Ingresos sin comisión
    income_res = await db.execute(
        select(Transaction).where(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.id.notin_(existing_ids) if existing_ids else True
        )
    )
    incomes = income_res.scalars().all()

    total_generated = 0
    for tx in incomes:
        commissions = await calculate_commissions_for_income(db, tx.id)
        total_generated += len(commissions)

    await db.commit()
    return {"message": f"Generadas {total_generated} comisiones para {len(incomes)} ingresos"}


@router.get("/commissions/recipient/{recipient_id}/summary", response_model=RecipientSummary)
async def get_recipient_summary(recipient_id: UUID, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CommissionRecipient).where(CommissionRecipient.id == recipient_id))
    recipient = r.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient not found")

    commissions_res = await db.execute(
        select(Commission).where(Commission.recipient_id == recipient_id)
    )
    all_comm = commissions_res.scalars().all()

    total_base = sum(float(c.base_amount) for c in all_comm)
    total_pending = sum(float(c.commission_amount) for c in all_comm if c.status == CommissionStatus.PENDING)
    total_paid = sum(float(c.commission_amount) for c in all_comm if c.status == CommissionStatus.PAID)
    total = total_pending + total_paid
    cumplimiento = (total_paid / total * 100) if total > 0 else 0.0

    return RecipientSummary(
        recipient_id=recipient_id,
        recipient_name=recipient.name,
        total_base=total_base,
        total_pendiente=total_pending,
        total_pagado=total_paid,
        porcentaje_cumplimiento=round(cumplimiento, 2)
    )


# ── Dashboard Widget ───────────────────────────────────────────────────────────

@router.get("/dashboard/commissions-summary", response_model=CommissionsDashboard)
async def get_commissions_summary(company_id: UUID, db: AsyncSession = Depends(get_db)):
    # Totales
    pending_res = await db.execute(
        select(func.sum(Commission.commission_amount))
        .where(Commission.company_id == company_id, Commission.status == CommissionStatus.PENDING)
    )
    total_pending = float(pending_res.scalar() or 0)

    paid_res = await db.execute(
        select(func.sum(Commission.commission_amount))
        .where(Commission.company_id == company_id, Commission.status == CommissionStatus.PAID)
    )
    total_paid = float(paid_res.scalar() or 0)

    # Top recipients
    recipients_res = await db.execute(
        select(CommissionRecipient).where(
            CommissionRecipient.company_id == company_id, CommissionRecipient.is_active == True
        )
    )
    all_recipients = recipients_res.scalars().all()

    top_list = []
    for rec in all_recipients:
        comm_res = await db.execute(
            select(Commission).where(Commission.recipient_id == rec.id)
        )
        comms = comm_res.scalars().all()
        total = sum(float(c.commission_amount) for c in comms)
        pending = sum(float(c.commission_amount) for c in comms if c.status == CommissionStatus.PENDING)
        if total > 0:
            top_list.append(TopRecipient(name=rec.name, total=total, pending=pending))

    top_list.sort(key=lambda x: x.total, reverse=True)

    return CommissionsDashboard(
        total_pendiente=total_pending,
        total_pagado=total_paid,
        top_recipients=top_list[:5]
    )
