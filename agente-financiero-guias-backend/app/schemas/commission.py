"""
schemas/commission.py
─────────────────────
Schemas Pydantic para el módulo de comisiones.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import CommissionStatus, RecipientType


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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


# ── Commissions ────────────────────────────────────────────────────────────────

class CommissionResponse(BaseModel):
    """Comisión con datos enriquecidos del recipient, cliente y servicio."""
    id: UUID
    company_id: UUID
    income_transaction_id: UUID
    commission_rule_id: Optional[UUID] = None
    recipient_id: UUID
    recipient_name: Optional[str] = None          # JOIN desde commission_recipients
    client_id: str
    client_name: Optional[str] = None             # JOIN desde clients
    service_id: str
    service_name: Optional[str] = None            # JOIN desde services
    base_amount: float                             # Subtotal sin IVA
    commission_amount: float
    status: CommissionStatus
    payment_transaction_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PayCommissionRequest(BaseModel):
    """Body para POST /commissions/{id}/pay"""
    payment_method: str = "transfer"
    payment_date: date = Field(default_factory=date.today)
    actual_amount: Optional[float] = Field(
        None,
        description="Si se omite, usa commission_amount. Útil para ajustes.",
        ge=0,
    )
    payment_method_id: Optional[str] = Field(
        None,
        description="ID del medio de pago (tabla payment_methods). Opcional.",
    )
    description: Optional[str] = None


class PayCommissionResponse(BaseModel):
    """Respuesta al pagar una comisión."""
    commission_id: UUID
    transaction_id: UUID
    amount_paid: float
    payment_method: str
    payment_date: date
    message: str = "Comisión pagada exitosamente"


# ── Generate Report ────────────────────────────────────────────────────────────

class GenerateCommissionsResponse(BaseModel):
    transactions_procesadas: int
    comisiones_generadas: int
    message: str


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
    recipient_id: UUID
    name: str
    total_comisiones: float
    total_pendiente: float
    total_pagado: float


class CommissionsDashboard(BaseModel):
    total_pendiente: float
    total_pagado: float
    recipient_count: int = 0
    top_recipients: List[TopRecipient]
