from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from uuid import UUID
from datetime import datetime, date
from typing import Literal, Any

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
    actual_amount_collected: float | None = None
    payment_method_id: str | None = None
    transaction_date: str | None = None
    # Legacy field kept for backward compatibility
    actual_amount: float | None = None
    payment_method: str = "transfer"

class IncomeBudgetResponse(BaseModel):
    id: UUID
    company_id: UUID
    client_id: str
    service_id: str
    # original backend field
    budgeted_amount: float
    actual_amount: float | None = None
    planned_date: date
    period_month: int
    period_year: int
    is_recurring: bool
    status: str
    transaction_id: UUID | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    # Frontend-compatible aliases (computed)
    amount: float = 0.0
    description: str | None = None
    client_name: str | None = None
    service_name: str | None = None

    @model_validator(mode='after')
    def compute_aliases(self) -> 'IncomeBudgetResponse':
        self.amount = self.budgeted_amount
        self.description = self.notes
        return self

    model_config = ConfigDict(from_attributes=True)

class IncomeSummary(BaseModel):
    total_budgeted: float
    total_collected: float
    total_pending: float
    pct_collected: float
    pending_count: int
