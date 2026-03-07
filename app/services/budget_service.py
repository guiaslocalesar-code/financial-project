from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from app.models.expense_budget import ExpenseBudget
from app.utils.enums import BudgetStatus

async def generate_recurrent_budgets(db: AsyncSession):
    """
    Finds all recurrent budgets from the previous month and creates copies for the current month.
    """
    # Simplified logic: 
    # 1. Get budgets from previous period (month/year) where is_recurring=True
    # 2. Duplicate them for the current period if they don't exist yet.
    
    # Let's use current month
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    last_period = today - relativedelta(months=1)
    
    result = await db.execute(
        select(ExpenseBudget).where(
            ExpenseBudget.is_recurring == True,
            ExpenseBudget.period_month == last_period.month,
            ExpenseBudget.period_year == last_period.year
        )
    )
    recurrent_templates = result.scalars().all()
    
    count = 0
    for template in recurrent_templates:
        # Check if already exists for current month
        exists = await db.execute(
            select(ExpenseBudget).where(
                ExpenseBudget.company_id == template.company_id,
                ExpenseBudget.expense_category_id == template.expense_category_id,
                ExpenseBudget.period_month == current_month,
                ExpenseBudget.period_year == current_year
            )
        )
        if not exists.scalar_one_or_none():
            new_budget = ExpenseBudget(
                company_id=template.company_id,
                expense_type_id=template.expense_type_id,
                expense_category_id=template.expense_category_id,
                description=template.description,
                budgeted_amount=template.budgeted_amount,
                planned_date=template.planned_date + relativedelta(months=1),
                period_month=current_month,
                period_year=current_year,
                is_recurring=True,
                status=BudgetStatus.PENDING
            )
            db.add(new_budget)
            count += 1
            
    if count > 0:
        await db.commit()
    
    return count
