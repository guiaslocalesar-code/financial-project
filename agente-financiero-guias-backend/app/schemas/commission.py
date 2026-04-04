from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date

class CommissionRuleBase(BaseModel):
    client_id: str | None = None
    service_id: str | None = None
    percentage: float

class CommissionRuleCreate(CommissionRuleBase):
    recipient_id: str | UUID

class CommissionRuleUpdate(BaseModel):
    client_id: str | None = None
    service_id: str | None = None
    percentage: float | None = None

class CommissionRuleResponse(CommissionRuleBase):
    id: str | UUID
    recipient_id: str | UUID
    created_at: datetime
    updated_at: datetime | None = None
    recipient_name: str | None = None
    client_name: str | None = None
    service_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CommissionRecipientBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str | None = Field(None, max_length=255)
    # These fields may not exist in older DB schemas, keep optional
    cuit: str | None = None
    is_active: bool | None = None
    type: str | None = None

class CommissionRecipientCreate(CommissionRecipientBase):
    company_id: str | UUID

class CommissionRecipientUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    cuit: str | None = None
    is_active: bool | None = None
    type: str | None = None

class CommissionRecipientResponse(CommissionRecipientBase):
    id: str | UUID
    company_id: str | UUID
    created_at: datetime
    updated_at: datetime | None = None
    rules: list[CommissionRuleResponse] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CommissionBase(BaseModel):
    transaction_id: str | UUID
    recipient_id: str | UUID
    amount: float
    base_amount: float | None = None
    commission_percentage: float | None = None
    status: str = "PENDING"

class CommissionStatusUpdate(BaseModel):
    status: str

class CommissionResponse(CommissionBase):
    id: str | UUID
    created_at: datetime
    updated_at: datetime | None = None
    recipient_name: str | None = None
    client_name: str | None = None
    client_logo: str | None = None
    service_name: str | None = None
    transaction_description: str | None = None
    transaction_date: date | None = None
    was_invoiced: bool | None = None

    model_config = ConfigDict(from_attributes=True)

class CommissionPay(BaseModel):
    payment_method: str
    payment_method_id: str | UUID | None = None
    payment_date: date | None = None
    actual_amount: float | None = None

class BulkPayPayload(BaseModel):
    commission_ids: list[UUID]
    payment_method: str
    payment_method_id: str | UUID | None = None
    payment_date: date | None = None

class RecipientStats(BaseModel):
    total_earned: float = 0
    total_pending: float = 0
    performance_pct: float = 0

class RecipientSummary(CommissionRecipientResponse):
    stats: RecipientStats
    commissions: list[CommissionResponse] = []

class TopRecipient(BaseModel):
    id: str | UUID
    name: str
    total_earned: float

class CommissionsSummary(BaseModel):
    total_pending: float
    total_paid: float
    recipient_count: int
    top_recipients: list[TopRecipient] = []


