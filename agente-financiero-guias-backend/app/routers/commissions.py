"""
routers/commissions.py
──────────────────────
Router completo del módulo de comisiones.
Endpoints:
  CRUD Destinatarios  : POST/GET/PATCH/DELETE  /commission-recipients
  CRUD Reglas         : POST/GET/PATCH/DELETE  /commission-rules
  Comisiones          : GET  /commissions/pending
                        POST /commissions/{id}/pay
                        POST /commissions/generate
                        GET  /commissions/recipient/{id}/summary
  Dashboard widget    : GET  /dashboard/commissions-summary
"""

import logging
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.client import Client
from app.models.commission import Commission
from app.models.commission_recipient import CommissionRecipient
from app.models.commission_rule import CommissionRule
from app.models.service import Service
from app.schemas.commission import (
    CommissionRecipientCreate,
    CommissionRecipientResponse,
    CommissionRecipientUpdate,
    CommissionResponse,
    CommissionRuleCreate,
    CommissionRuleResponse,
    CommissionRuleUpdate,
    CommissionsDashboard,
    GenerateCommissionsResponse,
    PayCommissionRequest,
    PayCommissionResponse,
    RecipientSummary,
    TopRecipient,
)
from app.services.commission_service import (
    calculate_commissions_for_income,
    generate_missing_commissions,
    pay_commission,
)
from app.utils.enums import CommissionStatus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Commissions"])


# ── Helpers internos ──────────────────────────────────────────────────────────

async def _enrich_commissions(
    db: AsyncSession, commissions: list[Commission]
) -> list[CommissionResponse]:
    """
    Enriquece una lista de comisiones con nombres de recipient, cliente y servicio.
    Hace una sola consulta por entidad para evitar N+1.
    """
    if not commissions:
        return []

    # Recolectar IDs únicos
    recipient_ids = {c.recipient_id for c in commissions}
    client_ids = {c.client_id for c in commissions}
    service_ids = {c.service_id for c in commissions}

    # Batch fetch
    rec_map: dict[UUID, str] = {}
    if recipient_ids:
        rows = await db.execute(
            select(CommissionRecipient.id, CommissionRecipient.name)
            .where(CommissionRecipient.id.in_(recipient_ids))
        )
        rec_map = {r.id: r.name for r in rows}

    cli_map: dict[str, str] = {}
    if client_ids:
        rows = await db.execute(
            select(Client.id, Client.name).where(Client.id.in_(client_ids))
        )
        cli_map = {r.id: r.name for r in rows}

    svc_map: dict[str, str] = {}
    if service_ids:
        rows = await db.execute(
            select(Service.id, Service.name).where(Service.id.in_(service_ids))
        )
        svc_map = {r.id: r.name for r in rows}

    result = []
    for c in commissions:
        item = CommissionResponse.model_validate(c)
        item.recipient_name = rec_map.get(c.recipient_id)
        item.client_name = cli_map.get(c.client_id)
        item.service_name = svc_map.get(c.service_id)
        result.append(item)

    return result


# ── Commission Recipients CRUD ─────────────────────────────────────────────────
@router.post("/commissions/recipients", response_model=CommissionRecipientResponse)
async def create_recipient(
    body: CommissionRecipientCreate,
    db: AsyncSession = Depends(get_db),
):
    recipient = CommissionRecipient(**body.model_dump())
    db.add(recipient)
    await db.commit()
    await db.refresh(recipient)
    return recipient


@router.get("/commissions/recipients", response_model=List[CommissionRecipientResponse])
async def list_recipients(
    company_id: UUID,
    only_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    q = select(CommissionRecipient).where(CommissionRecipient.company_id == company_id)
    if only_active:
        q = q.where(CommissionRecipient.is_active == True)  # noqa: E712
    result = await db.execute(q)
    return result.scalars().all()


@router.patch(
    "/commissions/recipients/{recipient_id}",
    response_model=CommissionRecipientResponse,
)
async def update_recipient(
    recipient_id: UUID,
    body: CommissionRecipientUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CommissionRecipient).where(CommissionRecipient.id == recipient_id)
    )
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient no encontrado")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(recipient, field, value)
    await db.commit()
    await db.refresh(recipient)
    return recipient


@router.delete("/commissions/recipients/{recipient_id}", status_code=204)
async def delete_recipient(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CommissionRecipient).where(CommissionRecipient.id == recipient_id)
    )
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient no encontrado")
    recipient.is_active = False
    await db.commit()


# ── Commission Rules CRUD ──────────────────────────────────────────────────────
@router.post("/commissions/rules", response_model=CommissionRuleResponse)
async def create_rule(body: CommissionRuleCreate, db: AsyncSession = Depends(get_db)):
    # Verificar que el recipient exista
    r = await db.execute(
        select(CommissionRecipient).where(CommissionRecipient.id == body.recipient_id)
    )
    if not r.scalar_one_or_none():
        raise HTTPException(400, "Recipient no encontrado")
    try:
        rule = CommissionRule(**body.model_dump())
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule
    except Exception as e:
        await db.rollback()
        err = str(e)
        if "uq_commission_rule" in err or "unique" in err.lower():
            raise HTTPException(400, "Ya existe una regla para este recipient/cliente/servicio")
        raise HTTPException(500, f"Error interno: {err}")


@router.get("/commissions/rules", response_model=List[CommissionRuleResponse])
async def list_rules(
    company_id: UUID,
    only_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    q = select(CommissionRule).where(CommissionRule.company_id == company_id)
    if only_active:
        q = q.where(CommissionRule.is_active == True)  # noqa: E712
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/commissions/rules/{rule_id}", response_model=CommissionRuleResponse)
async def update_rule(
    rule_id: UUID,
    body: CommissionRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CommissionRule).where(CommissionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Regla no encontrada")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/commissions/rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommissionRule).where(CommissionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Regla no encontrada")
    rule.is_active = False
    await db.commit()


# ── Commissions Management ─────────────────────────────────────────────────────

@router.get("/commissions", response_model=List[CommissionResponse])
async def list_commissions(
    company_id: UUID,
    status: Optional[CommissionStatus] = Query(None),
    recipient_id: Optional[UUID] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista las comisiones de una empresa.
    Opcionalmente filtra por status (ej: pending, paid) y/o recipient_id.
    Incluye nombre de destinatario, cliente y servicio (sin N+1).
    """
    q = select(Commission).where(Commission.company_id == company_id)
    
    if status:
        q = q.where(Commission.status == status)

    if recipient_id:
        q = q.where(Commission.recipient_id == recipient_id)

    if month:
        q = q.where(func.extract('month', Commission.created_at) == month)
    if year:
        q = q.where(func.extract('year', Commission.created_at) == year)

    q = q.order_by(Commission.created_at.desc())

    result = await db.execute(q)
    commissions = result.scalars().all()

    return await _enrich_commissions(db, commissions)


@router.post("/commissions/{commission_id}/pay", response_model=PayCommissionResponse)
async def pay_commission_endpoint(
    commission_id: UUID,
    body: PayCommissionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Paga una comisión pendiente de forma atómica.

    · Valida que la comisión exista y esté en estado PENDING.
    · Crea una Transaction de tipo EXPENSE (expense_origin = unbudgeted).
    · amount = actual_amount si se provee, sino commission_amount.
    · payment_method y payment_date vienen del frontend.
    · Guarda payment_transaction_id en la comisión.
    · Cambia status a PAID.
    · Si falla el commit, el estado NO se modifica (atómico).
    """
    try:
        expense_tx = await pay_commission(
            db=db,
            commission_id=commission_id,
            payment_method=body.payment_method,
            payment_date=body.payment_date,
            actual_amount=body.actual_amount,
            payment_method_id=body.payment_method_id,
            description=body.description,
        )
    except ValueError as e:
        msg = str(e)
        status_code = 404 if "no encontrada" in msg else 400
        raise HTTPException(status_code, msg)

    # Commit atómico: si falla aquí el estado de la comisión vuelve a PENDING
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error("Error al hacer commit del pago de comisión %s: %s", commission_id, e)
        raise HTTPException(500, "Error interno al guardar el pago. La comisión NO fue modificada.")

    return PayCommissionResponse(
        commission_id=commission_id,
        transaction_id=expense_tx.id,
        amount_paid=float(expense_tx.amount),
        payment_method=body.payment_method,
        payment_date=body.payment_date,
    )


@router.post("/commissions/generate", response_model=GenerateCommissionsResponse)
async def generate_commissions_endpoint(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Busca transactions de ingresos que todavía no tengan comisiones generadas
    y aplica las reglas vigentes.  Idempotente: no genera duplicados.
    """
    stats = await generate_missing_commissions(db, company_id)
    await db.commit()
    return GenerateCommissionsResponse(
        **stats,
        message=(
            f"Procesadas {stats['transactions_procesadas']} transacciones. "
            f"Generadas {stats['comisiones_generadas']} comisiones nuevas."
        ),
    )


@router.get(
    "/commissions/recipient/{recipient_id}/summary",
    response_model=RecipientSummary,
)
async def get_recipient_summary(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Resumen de comisiones para un destinatario:
      · total_base          — suma de bases (subtotales sin IVA sobre los que se calculó)
      · total_pendiente     — suma commission_amount de estado PENDING
      · total_pagado        — suma commission_amount de estado PAID
      · porcentaje_cumplimiento — total_pagado / (total_pendiente + total_pagado) × 100
    """
    r = await db.execute(
        select(CommissionRecipient).where(CommissionRecipient.id == recipient_id)
    )
    recipient = r.scalar_one_or_none()
    if not recipient:
        raise HTTPException(404, "Recipient no encontrado")

    # Agregados en una sola query por estado
    agg_res = await db.execute(
        select(
            Commission.status,
            func.sum(Commission.base_amount).label("sum_base"),
            func.sum(Commission.commission_amount).label("sum_commission"),
        )
        .where(Commission.recipient_id == recipient_id)
        .group_by(Commission.status)
    )
    rows = agg_res.all()

    total_base = 0.0
    total_pending = 0.0
    total_paid = 0.0

    for row in rows:
        total_base += float(row.sum_base or 0)
        if row.status == CommissionStatus.PENDING:
            total_pending += float(row.sum_commission or 0)
        elif row.status == CommissionStatus.PAID:
            total_paid += float(row.sum_commission or 0)

    total = total_pending + total_paid
    cumplimiento = (total_paid / total * 100) if total > 0 else 0.0

    return RecipientSummary(
        recipient_id=recipient_id,
        recipient_name=recipient.name,
        total_base=total_base,
        total_pendiente=total_pending,
        total_pagado=total_paid,
        porcentaje_cumplimiento=round(cumplimiento, 2),
    )


# ── Dashboard Widget ───────────────────────────────────────────────────────────

@router.get("/dashboard/commissions-summary", response_model=CommissionsDashboard)
async def get_commissions_summary(
    company_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Resumen de comisiones para el dashboard.
    Mapea a la lógica del dashboard_service para consistencia.
    """
    from app.services.dashboard_service import dashboard_service
    from datetime import date as py_date, timedelta
    
    # Defaults a mes actual si no hay fechas
    if not start_date:
        start_date = py_date.today().replace(day=1)
    if not end_date:
        # Calcular fin de mes
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
        
    summary = await dashboard_service.get_commissions_summary(company_id, start_date, end_date, db)
    return summary
