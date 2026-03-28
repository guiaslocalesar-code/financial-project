from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date
from app.database import get_db
from app.models.expense_budget import ExpenseBudget
from app.models.transaction import Transaction
from app.utils.enums import BudgetStatus, TransactionType

from app.schemas.expense_budget import ExpenseBudgetCreate, ExpenseBudgetResponse

router = APIRouter(prefix="/budgets", tags=["Expense Budgets"])

@router.post("", response_model=ExpenseBudgetResponse)
async def create_budget(budget_in: ExpenseBudgetCreate, db: AsyncSession = Depends(get_db)):
    # We now use Pydantic schema which parses strings to UUID/Date automatically
    budget = ExpenseBudget(**budget_in.model_dump())
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return budget

@router.get("", response_model=list[ExpenseBudgetResponse])
async def list_budgets(
    company_id: UUID, 
    month: int | None = Query(None, ge=1, le=12), 
    year: int | None = Query(None), 
    status: BudgetStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    actual_month = month or date.today().month
    actual_year = year or date.today().year

    query = select(ExpenseBudget).where(
        ExpenseBudget.company_id == company_id,
        ExpenseBudget.period_month == actual_month,
        ExpenseBudget.period_year == actual_year
    )
    if status:
        query = query.where(ExpenseBudget.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{budget_id}/pay")
async def pay_budget(budget_id: UUID, actual_amount: float | None = None, payment_method: str = "transfer", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExpenseBudget).where(ExpenseBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.status == BudgetStatus.PAID:
        raise HTTPException(status_code=400, detail="Budget already paid")

    final_amount = actual_amount if actual_amount is not None else budget.budgeted_amount
    
    # Create transaction
    transaction = Transaction(
        company_id=budget.company_id,
        budget_id=budget.id,
        expense_type_id=budget.expense_type_id,
        expense_category_id=budget.expense_category_id,
        type=TransactionType.EXPENSE,
        is_budgeted=True,
        amount=final_amount,
        payment_method=payment_method,
        description=f"Pago presupuesto: {budget.description}",
        transaction_date=date.today()
    )
    db.add(transaction)
    await db.flush() # Get transaction ID
    
    budget.status = BudgetStatus.PAID
    budget.actual_amount = final_amount
    budget.transaction_id = transaction.id
    
    await db.commit()
    return {"message": "Budget paid and transaction created", "transaction_id": transaction.id}
