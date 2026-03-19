from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Literal

class IncomeBudgetBase(BaseModel):
    company_id: UUID
    client_id: str
    service_id: str
    budgeted_amount: float
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool = True

class IncomeBudgetCreate(IncomeBudgetBase):
    pass

class IncomeBudgetUpdate(BaseModel):
    budgeted_amount: float | None = None
    actual_amount: float | None = None
    planned_date: date | None = None
    is_recurring: bool | None = None
    status: Literal["pending", "collected", "cancelled"] | None = None

class IncomeBudgetCollect(BaseModel):
    actual_amount: float | None = None   # Si None, usa budgeted_amount
    payment_method: str = "transfer"

class IncomeBudgetResponse(IncomeBudgetBase):
    id: UUID
    actual_amount: float | None = None
    status: str
    transaction_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IncomeSummary(BaseModel):
    total_budgeted: float
    total_collected: float
    total_pending: float
    pct_collected: float            # (total_collected / total_budgeted) * 100
    pending_count: int
