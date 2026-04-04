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
from app.schemas.income_budget import IncomeBudgetCreate, IncomeBudgetUpdate, IncomeBudgetResponse, IncomeBudgetCollect, IncomeSummary, IncomeBudgetGenerate
from app.services.commission_service import calculate_commissions_for_income
from typing import List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/income-budgets", tags=["Income Budgets"])



@router.post("", response_model=IncomeBudgetResponse)
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

@router.get("", response_model=List[IncomeBudgetResponse])
async def list_income_budgets(
    company_id: UUID, 
    month: int | None = Query(None, ge=1, le=12), 
    year: int | None = Query(None), 
    status: IncomeBudgetStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    from datetime import date as date_type
    actual_month = month or date_type.today().month
    actual_year = year or date_type.today().year

    query = select(IncomeBudget).where(
        IncomeBudget.company_id == company_id,
        IncomeBudget.period_month == actual_month,
        IncomeBudget.period_year == actual_year
    )
    if status:
        query = query.where(IncomeBudget.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{budget_id}/collect")
async def collect_income_budget(budget_id: UUID, collect_in: IncomeBudgetCollect, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IncomeBudget).where(IncomeBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Income budget not found")
    
    if budget.status == IncomeBudgetStatus.COLLECTED:
        raise HTTPException(status_code=400, detail="Budget already collected")

    # Resolve amount: support both legacy and new field
    raw_amount = collect_in.actual_amount_collected or collect_in.actual_amount or None
    
    # Base amount to calculate taxes if not provided
    base_to_collect = float(budget.budgeted_amount) + float(budget.iva_amount or 0.0)
    final_amount = float(raw_amount) if raw_amount is not None else base_to_collect

    # 2. Si requiere factura, emitir factura automáticamente con AFIP
    invoice_id = None
    if budget.requires_invoice:
        from app.models.company import Company
        from app.models.client import Client
        company = await db.execute(select(Company).where(Company.id == budget.company_id))
        company = company.scalar_one_or_none()
        client_res = await db.execute(select(Client).where(Client.id == budget.client_id))
        client = client_res.scalar_one_or_none()

        if not company or not client:
            raise HTTPException(status_code=400, detail="Faltan datos de la empresa o cliente para facturar")

        company_data = {"cuit": getattr(company, "cuit", "30000000000"), "point_of_sale": getattr(company, "afip_point_of_sale", 1)}
        invoice_data = {"client_cuit": client.cuit_cuil_dni, "invoice_type": "C"} 
        
        from app.services.afip_service import afip_service
        try:
            # Note: We use the budgeted_amount (NET) for the invoice items
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
            await db.flush() 
            
            item = InvoiceItem(
                invoice_id=invoice.id,
                service_id=budget.service_id,
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

    # Resolve transaction date
    tx_date = date.today()
    if collect_in.transaction_date:
        try:
            from datetime import datetime
            tx_date = datetime.strptime(collect_in.transaction_date, "%Y-%m-%d").date()
        except ValueError:
            pass

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
        amount=final_amount,
        payment_method=collect_in.payment_method,
        payment_method_id=collect_in.payment_method_id,
        description=f"Cobro presupuesto - {'Blanco' if budget.requires_invoice else 'Negro'}",
        transaction_date=tx_date
    )
    db.add(transaction)
    await db.flush() 
    
    budget.status = IncomeBudgetStatus.COLLECTED
    budget.actual_amount = final_amount
    budget.transaction_id = transaction.id
    
    # Logic A: Automatic Commissions using advanced service
    await calculate_commissions_for_income(db, transaction.id)
    
    await db.commit()
    return {
        "status": "success",
        "message": "Income collected and transaction created", 
        "transaction_id": str(transaction.id),
        "was_invoiced": budget.requires_invoice
    }

@router.post("/generate")
async def generate_income_budgets(generate_in: IncomeBudgetGenerate, db: AsyncSession = Depends(get_db)):
    """
    Standard generation logic using the frontend's expected schema.
    """
    from calendar import monthrange
    from app.models.client_service import ClientService
    from app.models.client import Client
    from app.utils.enums import ServiceStatus

    # 1. Fetch all ACTIVE client services for this company
    query = select(ClientService, Client).join(Client).where(
        Client.company_id == generate_in.company_id,
        Client.is_active == True,
        ClientService.status == ServiceStatus.ACTIVE
    )
    
    # Date filtering
    last_day_of_month = date(generate_in.year, generate_in.month, monthrange(generate_in.year, generate_in.month)[1])
    first_day_of_month = date(generate_in.year, generate_in.month, 1)
    
    query = query.where(ClientService.start_date <= last_day_of_month)
    query = query.where((ClientService.end_date == None) | (ClientService.end_date >= first_day_of_month))

    result = await db.execute(query)
    subs = result.all()

    created_count = 0
    skipped_count = 0

    for cs, client in subs:
        # Check idempotency
        exists_query = select(IncomeBudget).where(
            IncomeBudget.company_id == generate_in.company_id,
            IncomeBudget.client_id == client.id,
            IncomeBudget.service_id == cs.service_id,
            IncomeBudget.period_month == generate_in.month,
            IncomeBudget.period_year == generate_in.year
        )
        exists_result = await db.execute(exists_query)
        if exists_result.scalar_one_or_none():
            skipped_count += 1
            continue

        # Calculate IVA if the client requires invoice
        budgeted_amount = float(cs.monthly_fee)
        requires_invoice = client.requires_invoice
        iva_rate = 21.0 if requires_invoice else 0.0
        iva_amount = budgeted_amount * iva_rate / 100.0 if requires_invoice else 0.0

        # Create new budget
        new_budget = IncomeBudget(
            company_id=generate_in.company_id,
            client_id=client.id,
            service_id=cs.service_id,
            budgeted_amount=budgeted_amount,
            requires_invoice=requires_invoice,
            iva_rate=iva_rate,
            iva_amount=iva_amount,
            planned_date=first_day_of_month,
            period_month=generate_in.month,
            period_year=generate_in.year,
            is_recurring=True,
            status=IncomeBudgetStatus.PENDING,
            notes=f"Mensual {generate_in.month}/{generate_in.year}"
        )
        db.add(new_budget)
        created_count += 1

    if created_count > 0:
        await db.commit()
    
    return {
        "budgets_created": created_count,
        "budgets_skipped": skipped_count,
        "message": f"Se generaron {created_count} presupuestos de ingreso para {generate_in.month}/{generate_in.year}."
    }
