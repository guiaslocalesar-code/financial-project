from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from typing import Literal

class IncomeBudgetBase(BaseModel):
    company_id: UUID
    client_id: str
    service_id: str
    amount: float = Field(..., alias="budgeted_amount", validation_alias="budgeted_amount")
    budgeted_amount: float
    description: str | None = Field(None, alias="notes", validation_alias="notes")
    notes: str | None = None
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool = True

    model_config = ConfigDict(populate_by_name=True)

class IncomeBudgetCreate(BaseModel):
    company_id: UUID
    client_id: str
    service_id: str
    budgeted_amount: float
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool = True
    notes: str | None = None

class IncomeBudgetUpdate(BaseModel):
    budgeted_amount: float | None = None
    actual_amount: float | None = None
    planned_date: date | None = None
    is_recurring: bool | None = None
    status: Literal["pending", "collected", "cancelled"] | None = None
    notes: str | None = None

class IncomeBudgetCollect(BaseModel):
    actual_amount: float | None = None   # Si None, usa budgeted_amount
    payment_method: str = "transfer"

class IncomeBudgetResponse(IncomeBudgetBase):
    id: str
    actual_amount: float | None = None
    status: str
    transaction_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
    
    # Fallbacks para el frontend
    client_name: str | None = None
    service_name: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class IncomeSummary(BaseModel):
    total_budgeted: float
    total_collected: float
    total_pending: float
    pct_collected: float            # (total_collected / total_budgeted) * 100
    pending_count: int
