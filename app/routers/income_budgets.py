import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from datetime import date
from app.database import get_db
from app.models.income_budget import IncomeBudget
from app.models.client import Client
from app.models.client_service import ClientService
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.utils.enums import IncomeBudgetStatus, TransactionType, InvoiceStatus, ServiceStatus
from app.schemas.income_budget import IncomeBudgetCreate, IncomeBudgetUpdate, IncomeBudgetResponse, IncomeBudgetCollect, IncomeSummary
from app.services.commission_service import calculate_commissions_for_income
from typing import List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/income-budgets", tags=["Income Budgets"])


# ── Schema para el endpoint /generate ──────────────────────────────────────────

class GenerateIncomeBudgetsRequest(BaseModel):
    """Body para POST /income-budgets/generate"""
    company_id: UUID
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2024)


class GenerateIncomeBudgetsResponse(BaseModel):
    budgets_created: int
    budgets_skipped: int
    message: str


# ── Endpoints existentes ───────────────────────────────────────────────────────

@router.post("/", response_model=IncomeBudgetResponse)
async def create_income_budget(budget_in: IncomeBudgetCreate, db: AsyncSession = Depends(get_db)):
    budget = IncomeBudget(**budget_in.model_dump())
    if budget.requires_invoice and budget.iva_rate is not None:
        budget.iva_amount = float(budget.budgeted_amount) * float(budget.iva_rate) / 100.0
    else:
        budget.iva_amount = 0.0
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return budget

@router.get("/", response_model=List[IncomeBudgetResponse])
async def list_income_budgets(
    company_id: UUID, 
    month: int = Query(..., ge=1, le=12), 
    year: int = Query(...), 
    status: IncomeBudgetStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(IncomeBudget).where(
        IncomeBudget.company_id == company_id,
        IncomeBudget.period_month == month,
        IncomeBudget.period_year == year
    )
    if status:
        query = query.where(IncomeBudget.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()


# ── Generar presupuestos de ingresos del mes ───────────────────────────────────

@router.post("/generate", response_model=GenerateIncomeBudgetsResponse)
async def generate_income_budgets(
    body: GenerateIncomeBudgetsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera los presupuestos de ingresos (income_budgets) para un mes/año dado.

    Lógica:
    1. Busca todos los client_services con status = ACTIVE cuyo client
       también tenga is_active = True.
    2. Para cada uno, verifica que no exista ya un income_budget para ese
       mismo client + service + mes + año (idempotencia).
    3. Crea un income_budget en estado PENDING copiando el monthly_fee
       del contrato y los datos fiscales del cliente (requires_invoice, IVA).

    Diseñado para usarse con un botón en el frontend al inicio de cada mes.
    """
    target_month = body.month
    target_year = body.year
    company_id = body.company_id

    # 1. Traer todos los abonos activos de clientes activos de esta empresa
    query = (
        select(ClientService, Client)
        .join(Client, ClientService.client_id == Client.id)
        .where(
            Client.company_id == company_id,
            Client.is_active == True,
            ClientService.status == ServiceStatus.ACTIVE,
        )
    )
    result = await db.execute(query)
    active_subscriptions = result.all()

    if not active_subscriptions:
        return GenerateIncomeBudgetsResponse(
            budgets_created=0,
            budgets_skipped=0,
            message="No se encontraron abonos activos para esta empresa.",
        )

    created = 0
    skipped = 0

    for cs, client in active_subscriptions:
        # 2. Chequeo de idempotencia: ¿ya existe para este mes?
        exists_q = await db.execute(
            select(IncomeBudget.id).where(
                IncomeBudget.company_id == company_id,
                IncomeBudget.client_id == client.id,
                IncomeBudget.service_id == cs.service_id,
                IncomeBudget.period_month == target_month,
                IncomeBudget.period_year == target_year,
            )
        )
        if exists_q.scalar_one_or_none() is not None:
            skipped += 1
            continue

        # 3. Calcular IVA si el cliente requiere factura
        budgeted_amount = float(cs.monthly_fee)
        requires_invoice = client.requires_invoice
        iva_rate = 21.0 if requires_invoice else 0.0
        iva_amount = budgeted_amount * iva_rate / 100.0 if requires_invoice else 0.0

        # 4. Crear el presupuesto
        new_budget = IncomeBudget(
            company_id=company_id,
            client_id=client.id,
            service_id=cs.service_id,
            budgeted_amount=budgeted_amount,
            requires_invoice=requires_invoice,
            iva_rate=iva_rate,
            iva_amount=iva_amount,
            planned_date=date(target_year, target_month, 1),
            period_month=target_month,
            period_year=target_year,
            is_recurring=True,
            status=IncomeBudgetStatus.PENDING,
        )
        db.add(new_budget)
        created += 1

    if created > 0:
        await db.commit()

    logger.info(
        "Generados %d income_budgets para %d/%d (omitidos: %d)",
        created, target_month, target_year, skipped,
    )

    return GenerateIncomeBudgetsResponse(
        budgets_created=created,
        budgets_skipped=skipped,
        message=(
            f"Se generaron {created} presupuestos de ingreso para "
            f"{target_month}/{target_year}. "
            f"{skipped} ya existían y fueron omitidos."
        ),
    )


# ── Cobro de presupuesto ──────────────────────────────────────────────────────

@router.post("/{budget_id}/collect")
async def collect_income_budget(budget_id: UUID, collect_in: IncomeBudgetCollect, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IncomeBudget).where(IncomeBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Income budget not found")
    
    if budget.status == IncomeBudgetStatus.COLLECTED:
        raise HTTPException(status_code=400, detail="Budget already collected")

    # 2. Si requiere factura, emitir factura automáticamente con AFIP (Bloqueo estricto si falla)
    invoice_id = None
    if budget.requires_invoice:
        # Obtenemos info básica para facturar
        from app.models.company import Company
        from app.models.client import Client
        company = await db.execute(select(Company).where(Company.id == budget.company_id))
        company = company.scalar_one_or_none()
        client_res = await db.execute(select(Client).where(Client.id == budget.client_id))
        client = client_res.scalar_one_or_none()

        if not company or not client:
            raise HTTPException(status_code=400, detail="Faltan datos de la empresa o cliente para facturar")

        company_data = {"cuit": getattr(company, "cuit", "30000000000"), "point_of_sale": getattr(company, "punto_venta", 1)}
        invoice_data = {"client_cuit": client.cuit_cuil_dni, "invoice_type": "C"} # Simplificado temporalmente
        
        from app.services.afip_service import afip_service
        try:
            afip_res = await afip_service.emit_invoice(
                company_data, 
                invoice_data, 
                items=[{"description": budget.notes or f"Servicio {budget.service_id}", "amount": float(budget.budgeted_amount)}]
            )
            if afip_res.get("status") != "success":
                raise HTTPException(status_code=400, detail="Error en AFIP: No se pudo emitir la factura")
                
            from app.models.invoice import Invoice
            from app.models.invoice_item import InvoiceItem
            from app.utils.enums import InvoiceType, InvoiceStatus
            
            invoice = Invoice(
                company_id=budget.company_id,
                client_id=budget.client_id,
                invoice_type=InvoiceType.C,
                invoice_number=afip_res["invoice_number"],
                point_of_sale=company_data["point_of_sale"],
                cae=afip_res["cae"],
                cae_expiry=afip_res["cae_expiry"],
                subtotal=float(budget.budgeted_amount),
                iva_rate=float(budget.iva_rate or 0),
                iva_amount=float(budget.iva_amount or 0),
                total=float(budget.budgeted_amount) + float(budget.iva_amount or 0),
                status=InvoiceStatus.EMITTED,
                afip_raw_response=afip_res["raw_response"]
            )
            db.add(invoice)
            await db.flush() # Para obtener ID
            
            # Crear InvoiceItem
            item = InvoiceItem(
                invoice_id=invoice.id,
                service_id=budget.service_id, # service is uuid but might be string, handled by SQLAlchemy ForeignKey
                description=budget.notes or "Cobro de servicio",
                quantity=1.0,
                unit_price=float(budget.budgeted_amount),
                iva_rate=float(budget.iva_rate or 0),
                subtotal=float(budget.budgeted_amount)
            )
            db.add(item)
            await db.flush()
            
            invoice_id = invoice.id
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"AFIP API Error: {str(e)}")

    base_to_collect = float(budget.budgeted_amount) + float(budget.iva_amount or 0.0)
    transaction_amount = float(collect_in.actual_amount) if collect_in.actual_amount is not None else base_to_collect

    # Create transaction
    transaction = Transaction(
        company_id=budget.company_id,
        client_id=budget.client_id,
        invoice_id=invoice_id,
        income_budget_id=budget.id,
        service_id=budget.service_id,
        type=TransactionType.INCOME,
        is_budgeted=True,
        requires_invoice=budget.requires_invoice,
        iva_rate=budget.iva_rate,
        iva_amount=budget.iva_amount,
        amount=transaction_amount,
        payment_method=collect_in.payment_method,
        description=f"Cobro presupuesto servicio",
        transaction_date=date.today()
    )
    db.add(transaction)
    await db.flush() # Get transaction ID
    
    budget.status = IncomeBudgetStatus.COLLECTED
    budget.actual_amount = transaction_amount
    budget.transaction_id = transaction.id
    
    # Calcular comisiones automáticamente sobre el ingreso bruto
    await calculate_commissions_for_income(db, transaction.id)
    
    await db.commit()
    return {"message": "Income collected and transaction created", "transaction_id": transaction.id}
