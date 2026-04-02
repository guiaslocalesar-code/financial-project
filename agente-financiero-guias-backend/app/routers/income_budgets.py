from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date as date_type, datetime
from app.database import get_db
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.models.commission import Commission, CommissionRule, CommissionRecipient
from app.utils.enums import IncomeBudgetStatus, TransactionType, CommissionStatus
from app.schemas.income_budget import IncomeBudgetCreate, IncomeBudgetUpdate, IncomeBudgetResponse, IncomeBudgetCollect, IncomeSummary
from typing import List

router = APIRouter(prefix="/income-budgets", tags=["Income Budgets"])

@router.post("", response_model=IncomeBudgetResponse)
async def create_income_budget(budget_in: IncomeBudgetCreate, db: AsyncSession = Depends(get_db)):
    budget = IncomeBudget(**budget_in.model_dump())
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

    # Resolve amount: new field takes priority over legacy field
    raw_amount = collect_in.actual_amount_collected or collect_in.actual_amount or None
    final_amount = float(raw_amount) if raw_amount is not None else float(budget.budgeted_amount)

    # Resolve transaction date
    tx_date = date_type.today()
    if collect_in.transaction_date:
        try:
            tx_date = datetime.strptime(collect_in.transaction_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Read fiscal data from the budget
    requires_invoice = getattr(budget, 'requires_invoice', False) or False
    iva_rate = float(getattr(budget, 'iva_rate', 0) or 0)
    iva_amount = float(getattr(budget, 'iva_amount', 0) or 0)

    # --- STEP 1: Create INCOME Transaction ---
    transaction_kwargs = dict(
        company_id=budget.company_id,
        client_id=budget.client_id,
        income_budget_id=budget.id,
        service_id=budget.service_id,
        type=TransactionType.INCOME,
        is_budgeted=True,
        amount=final_amount,
        payment_method_id=collect_in.payment_method_id,
        description=f"Cobro presupuesto - {'Blanco (Facturado)' if requires_invoice else 'Negro (Sin Factura)'}",
        transaction_date=tx_date,
    )
    # Add fiscal fields if the columns exist in the model
    if hasattr(Transaction, 'requires_invoice'):
        transaction_kwargs['requires_invoice'] = requires_invoice
    if hasattr(Transaction, 'iva_rate'):
        transaction_kwargs['iva_rate'] = iva_rate
    if hasattr(Transaction, 'iva_amount'):
        transaction_kwargs['iva_amount'] = iva_amount

    transaction = Transaction(**transaction_kwargs)
    db.add(transaction)
    await db.flush()  # Get transaction.id

    # --- STEP 2: Auto-generate commissions (on NET base, not including IVA) ---
    # The commission base is the NET amount (budgeted_amount), not the total with IVA
    commission_base = float(budget.budgeted_amount)

    rules_query = select(CommissionRule).join(
        CommissionRecipient, CommissionRule.recipient_id == CommissionRecipient.id
    ).where(
        CommissionRecipient.company_id == budget.company_id
    )
    rules_result = await db.execute(rules_query)
    rules = rules_result.scalars().all()

    for rule in rules:
        match = False
        if rule.service_id and budget.service_id and str(rule.service_id) == str(budget.service_id):
            match = True
        elif rule.client_id and budget.client_id and str(rule.client_id) == str(budget.client_id):
            match = True
        elif not rule.service_id and not rule.client_id:
            match = True  # Global rule

        if match:
            comm_amount = (commission_base * float(rule.percentage)) / 100
            new_comm = Commission(
                transaction_id=transaction.id,
                recipient_id=rule.recipient_id,
                amount=comm_amount,
                status=CommissionStatus.PENDING
            )
            db.add(new_comm)

    # --- STEP 3: Close the budget ---
    budget.status = IncomeBudgetStatus.COLLECTED
    budget.actual_amount = final_amount
    budget.transaction_id = transaction.id

    await db.commit()

    return {
        "status": "success",
        "message": "Cobro registrado. Comisiones generadas automáticamente sobre el neto.",
        "data": {
            "transaction_id": str(transaction.id),
            "was_invoiced": requires_invoice,
        }
    }
