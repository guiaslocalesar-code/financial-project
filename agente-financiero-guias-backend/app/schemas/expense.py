from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import BudgetStatus

class ExpenseBase(BaseModel):
    company_id: UUID
    expense_type_id: UUID
    expense_category_id: UUID
    description: str
    budgeted_amount: float
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool = False

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    description: str | None = None
    budgeted_amount: float | None = None
    actual_amount: float | None = None
    planned_date: date | None = None
    status: BudgetStatus | None = None
    is_recurring: bool | None = None

class ExpenseResponse(ExpenseBase):
    id: UUID
    actual_amount: float | None = None
    status: BudgetStatus
    transaction_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
