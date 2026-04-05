from pydantic import BaseModel, ConfigDict, model_validator
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
    requires_invoice: bool = True
    iva_rate: float | None = 0.0
    iva_amount: float | None = 0.0
    is_recurring: bool = True
    notes: str | None = None

class IncomeBudgetCreate(IncomeBudgetBase):
    pass

class IncomeBudgetGenerate(BaseModel):
    company_id: UUID
    month: int
    year: int

class IncomeBudgetUpdate(BaseModel):
    budgeted_amount: float | None = None
    requires_invoice: bool | None = None
    iva_rate: float | None = None
    iva_amount: float | None = None
    actual_amount: float | None = None
    planned_date: date | None = None
    is_recurring: bool | None = None
    status: Literal["pending", "collected", "cancelled"] | None = None

class IncomeBudgetCollect(BaseModel):
    actual_amount_collected: float | None = None
    payment_method_id: str | None = None
    transaction_date: str | None = None
    actual_amount: float | None = None   # Legacy field
    payment_method: str = "transfer"      # Legacy field

class IncomeBudgetResponse(IncomeBudgetBase):
    id: UUID
    actual_amount: float | None = None
    status: str
    transaction_id: UUID | None = None
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
    pct_collected: float            # (total_collected / total_budgeted) * 100
    pending_count: int
