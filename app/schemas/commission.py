from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from app.utils.enums import RecipientType, CommissionStatus


# ── Commission Recipients ──────────────────────────────────────────────────────

class CommissionRecipientCreate(BaseModel):
    company_id: UUID
    type: RecipientType
    name: str
    cuit: Optional[str] = None
    email: Optional[str] = None

class CommissionRecipientUpdate(BaseModel):
    type: Optional[RecipientType] = None
    name: Optional[str] = None
    cuit: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class CommissionRecipientResponse(BaseModel):
    id: UUID
    company_id: UUID
    type: RecipientType
    name: str
    cuit: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Commission Rules ───────────────────────────────────────────────────────────

class CommissionRuleCreate(BaseModel):
    company_id: UUID
    recipient_id: UUID
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    percentage: float = Field(..., ge=0, le=100)
    priority: int = 1

class CommissionRuleUpdate(BaseModel):
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    percentage: Optional[float] = Field(None, ge=0, le=100)
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class CommissionRuleResponse(BaseModel):
    id: UUID
    company_id: UUID
    recipient_id: UUID
    client_id: Optional[str] = None
    service_id: Optional[str] = None
    percentage: float
    priority: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Commissions ────────────────────────────────────────────────────────────────

class CommissionResponse(BaseModel):
    id: UUID
    company_id: UUID
    income_transaction_id: UUID
    commission_rule_id: Optional[UUID] = None
    recipient_id: UUID
    recipient_name: Optional[str] = None      # joined from recipient
    client_id: str
    service_id: str
    base_amount: float
    commission_amount: float
    status: CommissionStatus
    payment_transaction_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Recipient Summary ──────────────────────────────────────────────────────────

class RecipientSummary(BaseModel):
    recipient_id: UUID
    recipient_name: str
    total_base: float
    total_pendiente: float
    total_pagado: float
    porcentaje_cumplimiento: float


# ── Dashboard Widget ───────────────────────────────────────────────────────────

class TopRecipient(BaseModel):
    name: str
    total: float
    pending: float

class CommissionsDashboard(BaseModel):
    total_pendiente: float
    total_pagado: float
    top_recipients: List[TopRecipient]
