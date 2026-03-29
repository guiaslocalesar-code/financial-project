from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.utils.enums import CommissionStatus

class CommissionRuleBase(BaseModel):
    client_id: str | None = None
    service_id: str | None = None
    percentage: float

class CommissionRuleCreate(CommissionRuleBase):
    recipient_id: str

class CommissionRuleResponse(CommissionRuleBase):
    id: str
    recipient_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommissionRecipientBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str | None = Field(None, max_length=255)

class CommissionRecipientCreate(CommissionRecipientBase):
    company_id: UUID

class CommissionRecipientResponse(CommissionRecipientBase):
    id: str
    company_id: UUID
    created_at: datetime
    rules: list[CommissionRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CommissionBase(BaseModel):
    transaction_id: UUID
    recipient_id: str
    amount: float
    status: CommissionStatus = CommissionStatus.PENDING

class CommissionResponse(CommissionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
