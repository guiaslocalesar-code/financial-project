from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Literal

from app.utils.enums import BudgetStatus

class ExpenseBudgetCreate(BaseModel):
    company_id: UUID
    expense_type_id: UUID
    expense_category_id: UUID
    description: str
    budgeted_amount: float
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool = False
    status: BudgetStatus = BudgetStatus.PENDING

class ExpenseBudgetResponse(BaseModel):
    id: UUID
    company_id: UUID
    expense_type_id: UUID
    expense_category_id: UUID
    description: str
    budgeted_amount: float
    actual_amount: float | None = None
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool
    status: BudgetStatus
    transaction_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
