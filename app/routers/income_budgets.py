from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date
from app.database import get_db
from app.models.income_budget import IncomeBudget
from app.models.transaction import Transaction
from app.utils.enums import IncomeBudgetStatus, TransactionType
from app.schemas.income_budget import IncomeBudgetCreate, IncomeBudgetUpdate, IncomeBudgetResponse, IncomeBudgetCollect, IncomeSummary
from app.services.commission_service import calculate_commissions_for_income
from typing import List

router = APIRouter(prefix="/income-budgets", tags=["Income Budgets"])

@router.post("/", response_model=IncomeBudgetResponse)
async def create_income_budget(budget_in: IncomeBudgetCreate, db: AsyncSession = Depends(get_db)):
    budget = IncomeBudget(**budget_in.model_dump())
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

@router.post("/{budget_id}/collect")
async def collect_income_budget(budget_id: UUID, collect_in: IncomeBudgetCollect, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IncomeBudget).where(IncomeBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Income budget not found")
    
    if budget.status == IncomeBudgetStatus.COLLECTED:
        raise HTTPException(status_code=400, detail="Budget already collected")

    final_amount = collect_in.actual_amount if collect_in.actual_amount is not None else budget.budgeted_amount
    
    # Create transaction
    transaction = Transaction(
        company_id=budget.company_id,
        client_id=budget.client_id,
        income_budget_id=budget.id,
        service_id=budget.service_id,
        type=TransactionType.INCOME,
        is_budgeted=True,
        amount=final_amount,
        payment_method=collect_in.payment_method,
        description=f"Cobro presupuesto servicio",
        transaction_date=date.today()
    )
    db.add(transaction)
    await db.flush() # Get transaction ID
    
    budget.status = IncomeBudgetStatus.COLLECTED
    budget.actual_amount = final_amount
    budget.transaction_id = transaction.id
    
    # Calcular comisiones automáticamente sobre el ingreso bruto
    await calculate_commissions_for_income(db, transaction.id)
    
    await db.commit()
    return {"message": "Income collected and transaction created", "transaction_id": transaction.id}
