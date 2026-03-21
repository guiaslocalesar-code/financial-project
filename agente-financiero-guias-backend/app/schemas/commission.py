from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.utils.enums import CommissionStatus

class CommissionRuleBase(BaseModel):
    client_id: UUID | None = None
    service_id: UUID | None = None
    percentage: float

class CommissionRuleCreate(CommissionRuleBase):
    recipient_id: UUID

class CommissionRuleResponse(CommissionRuleBase):
    id: UUID
    recipient_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommissionRecipientBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str | None = Field(None, max_length=255)

class CommissionRecipientCreate(CommissionRecipientBase):
    company_id: UUID

class CommissionRecipientResponse(CommissionRecipientBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    rules: list[CommissionRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CommissionBase(BaseModel):
    transaction_id: UUID
    recipient_id: UUID
    amount: float
    status: CommissionStatus = CommissionStatus.PENDING

class CommissionResponse(CommissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
