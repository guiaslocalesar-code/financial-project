from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import InvoiceType, InvoiceStatus

class InvoiceItemBase(BaseModel):
    service_id: UUID | None = None
    description: str
    quantity: float = 1.0
    unit_price: float
    iva_rate: float = 21.0

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemResponse(InvoiceItemBase):
    id: UUID
    subtotal: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvoiceBase(BaseModel):
    company_id: UUID
    client_id: UUID
    invoice_type: InvoiceType
    point_of_sale: int
    issue_date: date | None = None
    due_date: date | None = None
    currency: str = "ARS"
    exchange_rate: float = 1.0
    notes: str | None = None

class InvoiceCreate(InvoiceBase):
    items: list[InvoiceItemCreate]

class InvoiceUpdate(BaseModel):
    status: InvoiceStatus | None = None
    notes: str | None = None

class InvoiceResponse(InvoiceBase):
    id: UUID
    invoice_number: str | None = None
    cae: str | None = None
    cae_expiry: date | None = None
    subtotal: float
    iva_amount: float | None = None
    total: float
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime
    items: list[InvoiceItemResponse]

    model_config = ConfigDict(from_attributes=True)
