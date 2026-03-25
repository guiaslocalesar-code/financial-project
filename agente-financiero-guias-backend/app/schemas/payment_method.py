from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.utils.enums import PaymentMethodType

class PaymentMethodBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: PaymentMethodType
    bank: str | None = Field(None, max_length=100)
    is_credit: bool = False
    closing_day: int | None = Field(None, ge=1, le=31)
    due_day: int | None = Field(None, ge=1, le=31)

class PaymentMethodCreate(PaymentMethodBase):
    company_id: UUID

class PaymentMethodUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    type: PaymentMethodType | None = None
    bank: str | None = Field(None, max_length=100)
    is_credit: bool | None = None
    closing_day: int | None = Field(None, ge=1, le=31)
    due_day: int | None = Field(None, ge=1, le=31)
    is_active: bool | None = None

class PaymentMethodResponse(PaymentMethodBase):
    id: str
    company_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
