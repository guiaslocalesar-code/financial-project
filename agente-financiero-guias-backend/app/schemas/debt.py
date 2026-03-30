from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from app.utils.enums import DebtStatus, InterestType

class DebtInstallmentBase(BaseModel):
    installment_number: int
    amount: float
    due_date: date
    status: DebtStatus = DebtStatus.PENDING

class DebtInstallmentCreate(DebtInstallmentBase):
    debt_id: str | UUID

class DebtInstallmentResponse(DebtInstallmentBase):
    id: str | UUID
    debt_id: str | UUID
    transaction_id: str | UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DebtBase(BaseModel):
    description: str
    original_amount: float
    interest_type: InterestType | None = None
    interest_rate: float | None = None
    total_amount: float
    installments: int = 1

class DebtCreate(DebtBase):
    company_id: str | UUID

class DebtUpdate(BaseModel):
    description: str | None = None
    status: DebtStatus | None = None

class DebtResponse(DebtBase):
    id: str | UUID
    company_id: str | UUID
    status: DebtStatus
    created_at: datetime
    updated_at: datetime
    debt_installments: list[DebtInstallmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
