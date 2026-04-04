from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class PaymentMethodBase(BaseModel):
    id: str = Field(..., max_length=50) # Manual ID string like 'bank_transfer', 'cash', etc.
    name: str = Field(..., max_length=100)
    type: str # cash, bank, credit_card, etc.
    bank: str | None = Field(None, max_length=100)
    is_credit: bool = False
    closing_day: int | None = Field(None, ge=1, le=31)
    due_day: int | None = Field(None, ge=1, le=31)

class PaymentMethodCreate(PaymentMethodBase):
    company_id: UUID

class PaymentMethodUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: str | None = None
    bank: str | None = Field(None, max_length=100)
    is_credit: bool | None = None
    closing_day: int | None = Field(None, ge=1, le=31)
    due_day: int | None = Field(None, ge=1, le=31)
    is_active: bool | None = None

class PaymentMethodResponse(PaymentMethodBase):
    company_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
