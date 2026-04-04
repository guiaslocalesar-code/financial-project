from pydantic import BaseModel, Field, condecimal
from typing import List, Optional
from datetime import date
from uuid import UUID
from app.utils.enums import InvoiceType, InvoiceStatus

class InvoiceItemSchema(BaseModel):
    service_id: Optional[UUID] = None
    description: str
    quantity: float = Field(default=1.0)
    unit_price: float
    iva_rate: float = Field(default=21.0)

class InvoiceCreate(BaseModel):
    client_id: str # in db client id is string (VARCHAR 50)
    due_date: Optional[date] = None
    currency: str = Field(default="ARS")
    exchange_rate: float = Field(default=1.0)
    iva_rate: float = Field(default=21.0)
    notes: Optional[str] = None
    items: List[InvoiceItemSchema]

class InvoiceResponse(BaseModel):
    id: UUID
    company_id: UUID
    client_id: str
    invoice_type: InvoiceType
    status: InvoiceStatus
    point_of_sale: int
    invoice_number: Optional[str] = None
    cae: Optional[str] = None
    cae_expiry: Optional[date] = None
    issue_date: date
    due_date: Optional[date] = None
    subtotal: float
    iva_rate: float
    iva_amount: Optional[float] = None
    total: float
    currency: str
    exchange_rate: float
    notes: Optional[str] = None
    items: List[dict] = [] # Simplified nested items serialization
    
    class Config:
        from_attributes = True

class CancelResponse(BaseModel):
    status: str

class EmitResponse(BaseModel):
    id: UUID
    status: str
    invoice_number: str
    cae: str
    cae_expiry: date
    total: float
