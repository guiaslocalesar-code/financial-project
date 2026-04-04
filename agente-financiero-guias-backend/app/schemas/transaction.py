from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import TransactionType, ExpenseOrigin

class TransactionBase(BaseModel):
    company_id: UUID
    client_id: UUID | None = None
    invoice_id: UUID | None = None
    budget_id: UUID | None = None
    service_id: UUID | None = None
    expense_type_id: UUID | None = None
    expense_category_id: UUID | None = None
    type: TransactionType
    is_budgeted: bool = False
    expense_origin: ExpenseOrigin | None = None
    requires_invoice: bool = True
    iva_rate: float | None = 0.0
    iva_amount: float | None = 0.0
    amount: float
    currency: str = "ARS"
    exchange_rate: float = 1.0
    payment_method: str | None = None
    description: str | None = None
    transaction_date: date | None = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: float | None = None
    requires_invoice: bool | None = None
    iva_rate: float | None = None
    iva_amount: float | None = None
    payment_method: str | None = None
    description: str | None = None
    transaction_date: date | None = None

class TransactionResponse(TransactionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
