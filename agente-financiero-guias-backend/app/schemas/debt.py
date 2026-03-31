from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date

class DebtInstallmentBase(BaseModel):
    installment_number: int
    amount: float
    due_date: date
    status: str = "PENDING"
    capital_amount: float | None = None
    interest_amount: float | None = None

class DebtInstallmentCreate(DebtInstallmentBase):
    debt_id: str | UUID

class DebtInstallmentResponse(DebtInstallmentBase):
    id: str | UUID
    debt_id: str | UUID
    transaction_id: str | UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class DebtBase(BaseModel):
    description: str
    original_amount: float
    interest_type: str | None = None
    interest_rate: float | None = None
    interest_total: float | None = None
    total_amount: float
    installments: int = 1
    installment_amount: float | None = None
    first_due_date: date | None = None

class DebtCreate(DebtBase):
    company_id: str | UUID

class DebtUpdate(BaseModel):
    description: str | None = None
    status: str | None = None

class DebtResponse(DebtBase):
    id: str | UUID
    company_id: str | UUID
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    debt_installments: list[DebtInstallmentResponse] = []

    model_config = ConfigDict(from_attributes=True)

