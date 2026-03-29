from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import TransactionType, ExpenseOrigin, PaymentMethod

class TransactionBase(BaseModel):
    company_id: str | UUID
    client_id: str | None = None
    invoice_id: str | UUID | None = None
    budget_id: str | UUID | None = None
    service_id: str | None = None
    expense_type_id: str | UUID | None = None
    expense_category_id: str | UUID | None = None
    payment_method_id: str | None = None
    type: TransactionType
    is_budgeted: bool = False
    expense_origin: ExpenseOrigin | None = None
    amount: float
    currency: str = "ARS"
    exchange_rate: float = 1.0
    payment_method: PaymentMethod | None = None
    description: str | None = None
    transaction_date: date | None = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: float | None = None
    payment_method: PaymentMethod | None = None
    description: str | None = None
    transaction_date: date | None = None

class TransactionResponse(TransactionBase):
    id: str | UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
